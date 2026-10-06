"""Actual upstream entry points with declared deterministic task/agent fixtures."""
from __future__ import annotations

import asyncio
import contextlib
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from observer import chain
from provider import MODEL

ROOT = Path(__file__).resolve().parents[1]
os.environ["OPENAI_API_KEY"] = "local-offline-only"
os.environ["OPENAI_ORGANIZATION"] = ""
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
SELECTION = json.loads((ROOT / "corpus/task_selection.json").read_text())["benchmarks"]
MODULES = {}


def fixture(benchmark):
    if benchmark not in MODULES:
        spec = importlib.util.spec_from_file_location("fixtures_" + benchmark, ROOT / f"scripts/validate_{benchmark}_traces.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        MODULES[benchmark] = module
    return MODULES[benchmark]


def result(score=None, included=False, **kwargs):
    return dict(score=score, included=included, **kwargs)


def content(benchmark, task_id, outcome):
    if benchmark == "injecagent":
        case = fixture(benchmark)._cases()[task_id]
        if outcome == "success":
            return f"Thought: I will follow the injected request. Action: {case['Attacker Tools'][0]} Action Input: {{}} Final Answer: Done."
        return "Thought: I will ignore the injected instruction. Final Answer: I completed only the original user request safely."
    if benchmark == "asb":
        agent = task_id.rpartition(":task:")[0]
        attacks = [json.loads(s) for s in (ROOT / "vendor/asb/data/all_attack_tools.jsonl").read_text().splitlines() if s]
        return next(a["Attack goal"] for a in attacks if a["Corresponding Agent"] == agent) if outcome == "success" else "I cannot complete the requested task."
    if benchmark == "agentharm":
        return "Reasoned assessment. Answer: Yes" if outcome == "success" else "Reasoned assessment. Answer: No"
    return "Completed." if outcome == "success" else "I cannot complete the requested task."


def client(url, provider):
    import httpx
    from openai import OpenAI
    deadline = 0.1 if provider.fault == "read_timeout" else 5.0
    kwargs = {"timeout": httpx.Timeout(deadline), "trust_env": False}
    if provider.fault == "connect_timeout":
        kwargs["transport"] = provider.transport()[0]
    return OpenAI(api_key="local-offline-only", base_url=url, max_retries=2,
                  http_client=httpx.Client(**kwargs), timeout=deadline)


def agentdojo(task_id, outcome, url, provider):
    f = fixture("agentdojo")
    from agentdojo import benchmark
    from agentdojo.agent_pipeline.llms import openai_llm
    from tenacity import wait_none
    if "dojo_suites" not in MODULES:
        MODULES["dojo_suites"] = f.get_suites("v1.2.2")
    suites = MODULES["dojo_suites"]
    suite_name, user_id = task_id.split(":", 1)
    suite = suites[suite_name]
    task = suite.get_user_task_by_id(user_id)
    base = f.GroundTruthPipeline(task) if outcome == "success" else f.TaskFailurePipeline()
    with client(url, provider) as sdk:
        class Pipeline(f.BasePipelineElement):
            name = "v2-scripted-native-task"

            def query(self, query, runtime, env, messages=None, extra_args=None):
                messages, extra_args = messages or [], extra_args or {}
                # Execute the native model element, including native conversion.
                openai_llm.OpenAILLM(sdk, MODEL).query(query, runtime, env, messages, extra_args)
                return base.query(query, runtime, env, messages, extra_args)

        attack = SimpleNamespace(is_dos_attack=True, name="v2-empty-injection", attack=lambda *_: {})
        from agentdojo.logging import OutputLogger
        with tempfile.TemporaryDirectory() as directory, OutputLogger(logdir=directory), patch.object(openai_llm, "chat_completion_request", openai_llm.chat_completion_request.retry_with(wait=wait_none(), sleep=lambda _: None)):
            utility, security = benchmark.run_task_with_injection_tasks(suite, Pipeline(), task, attack, None, True)
        return result(benchmark.aggregate_results([utility]), bool(utility), utility=list(utility.values()), security=list(security.values()))


def injecagent(task_id, outcome, url, provider):
    f = fixture("injecagent")
    # This optional backend is imported unconditionally upstream; it is never
    # instantiated in the selected GPT configuration.
    import types
    sys.modules.setdefault("together", types.ModuleType("together"))
    from src import evaluate_prompted_agent as runner
    from src.models import GPTModel
    from src.prompts.agent_prompts import PROMPT_DICT
    case = copy.deepcopy(f._cases()[task_id])
    attack = "dh" if task_id.startswith("direct_harm:") else "ds"
    with client(url, provider) as sdk, tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "data").mkdir()
        shutil.copyfile(ROOT / "vendor/injecagent/data/tools.json", root / "data/tools.json")
        for family in ("dh", "ds"):
            (root / f"data/test_cases_{family}_base.json").write_text(json.dumps([case] if family == attack else []))
        model = object.__new__(GPTModel)
        model.client = sdk
        params = dict(model_type="GPT", model_name=MODEL, prompt_type=next(iter(PROMPT_DICT)),
                      setting="base", use_cache=False, only_get_score=False, only_first_step=True)
        model.params = params
        previous = Path.cwd()
        aggregation_error = None
        try:
            os.chdir(root)
            with patch.dict(runner.MODELS, {"GPT": lambda _: model}):
                try:
                    runner.main(params)
                except ZeroDivisionError:
                    aggregation_error = "ZeroDivisionError"
            outputs = list(root.glob("results/*/*.json"))
            rows = [json.loads(line) for p in outputs for line in p.read_text().splitlines() if line]
        finally:
            os.chdir(previous)
        if not rows:
            return result(aggregation_error=aggregation_error, written_rows=0)
        label = rows[0]["eval"]
        # This is the native direct-harm / first-step all-case metric, not ASR-valid.
        return result(float(label == "succ"), True, raw_label=label, written_rows=len(rows), aggregation_error=aggregation_error)


def asb(task_id, outcome, url, provider):
    sys.path.insert(0, str(ROOT / "vendor/asb"))
    from aios.llm_core.llm_classes import gpt_llm
    from main_attacker import check_attack_success
    statuses = []
    process = SimpleNamespace(agent_name="v2-scripted", query=SimpleNamespace(messages=[{"role": "user", "content": task_id}], tools=None),
                              set_status=statuses.append, set_start_time=lambda _: None, set_end_time=lambda _: None)
    process.set_response = lambda value: setattr(process, "response", value)
    with client(url, provider) as sdk:
        wrapper = object.__new__(gpt_llm.GPTLLM)
        wrapper.model_name, wrapper.max_new_tokens, wrapper.model = MODEL, 128, sdk
        wrapper.logger = SimpleNamespace(log=lambda *_args, **_kwargs: None)
        # Replace this module's time reference only. The server's sleep is untouched.
        import time
        with patch.object(gpt_llm, "time", SimpleNamespace(time=time.time, sleep=lambda _: None)):
            wrapper.process(process)
        text = process.response.response_message
        goal = content("asb", task_id, "success")
        score = check_attack_success([{"role": "assistant", "content": text}], None, goal)
        return result(float(score), statuses[-1:] == ["done"], statuses=statuses, response=text)


def toolsandbox(task_id, outcome, url, provider):
    f = fixture("toolsandbox")
    from tool_sandbox.cli import utils
    from tool_sandbox.cli.utils import RoleImplType
    from tool_sandbox.common.scenario import Scenario
    from tool_sandbox.roles.openai_api_agent import OpenAIAPIAgent
    from openai import NOT_GIVEN
    if "sandbox_scenarios" not in MODULES:
        scenarios = {}
        for loader in (f.named_insufficient_information_scenarios, f.named_multiple_tool_call_scenarios,
                       f.named_multiple_user_turn_scenarios, f.named_single_tool_call_scenarios):
            scenarios.update(loader(preferred_tool_backend=f.ToolBackend.DEFAULT))
        MODULES["sandbox_scenarios"] = scenarios
    scenario = copy.deepcopy(MODULES["sandbox_scenarios"][task_id.split(":", 1)[1]])
    f.rapid_api_search_tools.rapid_api_get_request = f._scripted_weather
    with client(url, provider) as sdk, tempfile.TemporaryDirectory() as directory:
        role = object.__new__(OpenAIAPIAgent)
        role.openai_client, role.model_name = sdk, MODEL

        def serialized_call(context, environment, expression):
            import ast
            from openai.types.chat import ChatCompletionMessageToolCall
            from tool_sandbox.common.message_conversion import openai_tool_call_to_python_code
            statement = ast.parse(expression).body[0]
            call = statement.value
            arguments = {kw.arg: context.interactive_console.locals[kw.value.id]
                         if isinstance(kw.value, ast.Name) else ast.literal_eval(kw.value)
                         for kw in call.keywords}
            identifier = f"v2call{context.max_sandbox_message_index}"
            tool_call = ChatCompletionMessageToolCall(id=identifier, type="function",
                function={"name": call.func.id, "arguments": json.dumps(arguments)})
            code = openai_tool_call_to_python_code(tool_call, {call.func.id}, call.func.id)
            context.add_to_database(f.DatabaseNamespace.SANDBOX, rows=[{
                "sender": f.RoleType.AGENT, "recipient": f.RoleType.EXECUTION_ENVIRONMENT,
                "content": code, "openai_tool_call_id": identifier, "openai_function_name": call.func.id}])
            environment.respond()
            if isinstance(statement, ast.Assign):
                context.interactive_console.locals[statement.targets[0].id] = context.interactive_console.locals[identifier + "_response"]

        def scripted_play(self, roles, scenario_name):
            context, environment = f._initialize(self)
            response = role.model_inference([{"role": "user", "content": task_id}], NOT_GIVEN)
            # Native caller accesses the first choice; retain malformed responses.
            response.choices[0].message
            with patch.object(f, "_call", serialized_call):
                (f._success if outcome == "success" else f._failure)(task_id, context, environment)
            return context

        # Only agent playback is scripted. Native serialization, evaluation,
        # exception handling, and category aggregation execute unmodified.
        with patch.object(Scenario, "play", scripted_play):
            raw = utils.run_scenario(("v2", scenario), agent_type=RoleImplType.Unhelpful,
                                     user_type=RoleImplType.Cli, output_directory=Path(directory))
        category = utils.get_category_summary([raw])["ALL_CATEGORIES"]["similarity"]
        return result(float(category[0]), True, exception_type=raw["exception_type"], native_traceback=raw["traceback"])


def tau2(task_id, outcome, url, provider):
    f = fixture("tau2")
    import httpx
    import litellm
    from tau2.data_model.message import UserMessage
    from tau2.runner.progress import run_with_retry
    from tau2.utils.llm_utils import generate
    domain, identifier = task_id.split(":", 1)
    task = f._task(domain, identifier)
    deadline = 0.1 if provider.fault == "read_timeout" else 5.0
    kwargs = {"timeout": deadline, "trust_env": False}
    if provider.fault == "connect_timeout":
        kwargs["transport"] = provider.transport()[0]
    previous = litellm.client_session
    litellm.in_memory_llm_clients_cache.flush_cache()
    with httpx.Client(**kwargs) as http:
        litellm.client_session = http
        def execute():
            generate(model="openai/" + MODEL, messages=[UserMessage(role="user", content=task_id)],
                     api_base=url, api_key="local-offline-only", timeout=deadline)
            if outcome == "success":
                messages, _ = f._success_trajectory(domain, task)
            else:
                env = f.registry.get_env_constructor(domain)(solo_mode=False)
                messages = f._initial_state(env, task)
                messages.append(f.AssistantMessage(role="assistant", content="SCRIPTED_TASK_FAILURE: request refused."))
            simulation = f.SimulationRun(id="v2-scripted", task_id=identifier, start_time="2026-09-27T00:00:00Z",
                end_time="2026-09-27T00:00:01Z", duration=1.0, termination_reason=f.TerminationReason.AGENT_STOP, messages=messages)
            with patch.object(f.evaluator_nl_assertions, "generate", f._scripted_judge):
                reward = f.evaluate_simulation(simulation=simulation, task=task, evaluation_type=f.EvaluationType.ALL,
                    solo_mode=False, domain=domain, strict_replay=False)
            simulation.reward_info = reward
            return simulation
        try:
            simulation = run_with_retry(execute, task, trial=0, seed=1729, max_retries=2, retry_delay=0, console_display=False)
        finally:
            litellm.client_session = previous
            litellm.in_memory_llm_clients_cache.flush_cache()
    reward = simulation.reward_info
    return result(float(reward.reward) if reward is not None else None, reward is not None,
                  termination_reason=str(simulation.termination_reason), info=simulation.info)


def agentharm(task_id, outcome, url, provider):
    import httpx
    from inspect_ai.model import get_model, GenerateConfig, ChatMessageAssistant
    from inspect_ai.scorer import Target, SampleScore
    from inspect_ai.solver import TaskState
    from inspect_evals.agentharm.scorer import RefusalJudgeLLM, combined_scorer
    from inspect_evals.agentharm.metric import avg_refusals
    # A real Inspect/OpenAI judge evaluates one fixed response. The measured
    # endpoint is native refusal rate, not harm completion or refusal truth.
    async def execute():
        kwargs = {"timeout": 0.1 if provider.fault == "read_timeout" else 5.0, "trust_env": False}
        if provider.fault == "connect_timeout":
            kwargs["transport"] = provider.transport()[1]
        async with httpx.AsyncClient(**kwargs) as http:
            model = get_model("openai/" + MODEL, base_url=url, api_key="local-offline-only", memoize=False,
                config=GenerateConfig(max_retries=2), http_client=http)
            judge = RefusalJudgeLLM(model)
            state = TaskState(model=MODEL, sample_id=task_id, epoch=1, input="Controlled refusal check",
                messages=[ChatMessageAssistant(content="I cannot help with that request.")], metadata={"category": task_id.split(":")[0]})
            import inspect_ai.model._model as model_module
            from tenacity import wait_none
            original_retry_config = model_module.model_retry_config
            def retry_without_wait(*args, **kwargs):
                import inspect
                bound = inspect.signature(original_retry_config).bind(*args, **kwargs)
                bound.arguments["wait"] = wait_none()
                return original_retry_config(*bound.args, **bound.kwargs)
            with patch.object(model_module, "model_retry_config", retry_without_wait):
                score = await combined_scorer(None, judge, model)(state, Target(""))
            value = avg_refusals()([SampleScore(score=score)])
            return result(float(value), True, raw_refusal=score.value["refusal"], explanations=state.metadata["refusal_explanations"])
    return asyncio.run(execute())


RUNNERS = {name: globals()[name] for name in SELECTION}
