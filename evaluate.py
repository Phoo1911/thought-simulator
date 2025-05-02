import os
import json
import yaml
import time
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import matplotlib.pyplot as plt
import seaborn as sns
import re
# Load environment variables (API key)
load_dotenv()
client = OpenAI()

# === Configuration ===
GEN_MODEL = "gpt-3.5-turbo"
JUDGE_MODEL = "gpt-4o"
TEMPERATURE = 0
N_SAMPLES = 3  # Number of samples per condition
BASELINE = "baseline_cot.hierarchical_structure"

PATTERNS = [
    # 의사결정 패턴
    "decision_making.hierarchical_structure",
    #"decision_making.multiple_perspective",
    #"decision_making.self_reflective",

    # 윤리적 추론 패턴
    #"ethical_reasoning.hierarchical_structure",
    #"ethical_reasoning.multiple_perspective",
    #"ethical_reasoning.self_reflective",

    # 창의적 사고 패턴
    #"creative_thinking.hierarchical_structure",
    #"creative_thinking.multiple_perspective",
    #"creative_thinking.self_reflective",

    # 가설적 시나리오 분석 패턴
    #"hypothetical_scenario.hierarchical_structure",
    #"hypothetical_scenario.multiple_perspective",
    #"hypothetical_scenario.self_reflective",
]

SCENARIOS = {
    "decision": "Develop a strategy for entering a new business market.",
    #"ethics": "Resolve the ethical dilemma of self-driving cars.",
    #"creative": "Propose innovative ways to utilize urban spaces.",
    #"scenario": "Predict the long-term effects of climate change."
}

# === Load YAML Prompt Templates ===
with open("templates.yaml", encoding="utf-8") as f:
    TEMPLATES = yaml.safe_load(f)

def get_template(path: str) -> str:
    node = TEMPLATES
    for key in path.split("."):
        if key not in node:
            raise KeyError(f"Invalid template path: {path}")
        node = node[key]
    return node

def render_template(path: str, scenario: str, depth=5, detail=5, priorities="-") -> str:
    block = get_template(path)
    if isinstance(block, dict):
        block = block.get("meta_level", "") + block.get("structure_level", "") + block.get("content_level", "")
    return (block.replace("${scenario}", scenario)
                 .replace("${depth}", str(depth))
                 .replace("${detail}", str(detail))
                 .replace("${priorities}", priorities))

def gpt_call(model: str, prompt: str, system_prompt: str = "", retries=3) -> str:
    messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
    messages.append({"role": "user", "content": prompt})

    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=TEMPERATURE,
                messages=messages,
                timeout=60
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ GPT call failed (attempt {attempt + 1}): {e}")
            time.sleep(3)
    return ""



def judge_pairwise(resp_a: str, resp_b: str) -> dict:
    judge_prompt = f"""
Criteria: logic, diversity, metacognition, and stepwise thinking (each scored 1–5).
Return JSON format: {{"better": "A/B", "logic": x, "diversity": x, "meta": x, "step": x}}

Response A:
{resp_a}

Response B:
{resp_b}
"""
    response = gpt_call(JUDGE_MODEL, judge_prompt, system_prompt="You are a strict evaluator. Output valid JSON only.")
    
    # 🔧 JSON 정리: 코드블럭 제거
    response = re.sub(r"```json|```", "", response).strip()
    
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("⚠️ Invalid JSON from judge (after cleanup):\n", response[:300])
        return {"better": "-", "logic": 0, "diversity": 0, "meta": 0, "step": 0}


def run_evaluation():
    pairwise_records = []

    for s_key, s_text in SCENARIOS.items():
        for pat_path in PATTERNS:
            for i in range(N_SAMPLES):
                try:
                    base_prompt = render_template(BASELINE, s_text)
                    pat_prompt = render_template(pat_path, s_text)

                    resp_base = gpt_call(GEN_MODEL, base_prompt)
                    resp_pat = gpt_call(GEN_MODEL, pat_prompt)

                    judge_result = judge_pairwise(resp_base, resp_pat)
                    pairwise_records.append({
                        "scenario": s_key,
                        "pattern": pat_path,
                        "A_name": BASELINE,
                        "B_name": pat_path,
                        "A_output": resp_base,
                        "B_output": resp_pat,
                        "better": judge_result.get("better", "-"),
                        "logic": judge_result.get("logic", 0),
                        "diversity": judge_result.get("diversity", 0),
                        "meta": judge_result.get("meta", 0),
                        "step": judge_result.get("step", 0)
                    })

                    time.sleep(2)  # Respect rate limits
                except KeyError as e:
                    print(f"❌ Skipping invalid pattern: {pat_path} -> {e}")

    # Save results
    os.makedirs("results", exist_ok=True)
    pd.DataFrame(pairwise_records).to_csv("results/pairwise_judgment.csv", index=False)
    print("✓ Pairwise evaluation complete. Saved to `results/pairwise_judgment.csv`")

# Run
run_evaluation()

# === Visualization (Baseline vs. Patterns) ===
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# 데이터 로드
df = pd.read_csv("results/pairwise_judgment.csv")

# 평가 기준
criteria = ["logic", "diversity", "meta", "step"]

# A: baseline / B: pattern
baseline_scores = df.groupby("B_name")[criteria].mean().reset_index()
baseline_scores = baseline_scores.rename(columns={"B_name": "pattern"})

# baseline 기준점 계산
base_only = df[df["B_name"] == "baseline_cot.hierarchical_structure"]
base_mean = base_only[criteria].mean()

# 차이 계산
for col in criteria:
    baseline_scores[col + "_delta"] = baseline_scores[col] - base_mean[col]

# 시각화: 각 기준별로 score 차이 시각화
melted = baseline_scores.melt(id_vars="pattern", 
                              value_vars=[c + "_delta" for c in criteria],
                              var_name="criterion", value_name="score_diff")

# 기준 이름 깔끔하게
melted["criterion"] = melted["criterion"].str.replace("_delta", "").str.capitalize()

# Plot
plt.figure(figsize=(12, 6))
sns.barplot(data=melted, x="score_diff", y="pattern", hue="criterion")
plt.axvline(0, color="gray", linestyle="--")
plt.title("Δ Evaluation Scores Compared to Baseline")
plt.xlabel("Score Difference (vs. Baseline)")
plt.ylabel("Prompt Pattern")
plt.legend(title="Criterion")
plt.tight_layout()
plt.savefig("results/evaluation_diff_chart.png")
plt.show()

print("✓ Baseline comparison visualization complete. Saved to `results/evaluation_diff_chart.png`")

