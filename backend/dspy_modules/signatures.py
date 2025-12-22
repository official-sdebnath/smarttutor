import dspy
from dspy import Signature, InputField, OutputField


# -------------------------
# Signatures
# -------------------------


class AnswerEvaluation(Signature):
    question: str = InputField()
    answer: str = InputField()
    evidence: str = InputField()

    score: float = OutputField(desc="Score between 0 and 1")
    reasoning: str = OutputField(desc="Short justification")


class RewriteAnswer(Signature):
    answer: str = InputField()
    rewrite_instructions: str = InputField()

    rewritten_answer: str = OutputField()


# -------------------------
# Modules
# -------------------------


class EvaluatorModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.evaluate = dspy.Predict(AnswerEvaluation)

    def __call__(self, question, answer, evidence):
        return self.evaluate(
            question=question,
            answer=answer,
            evidence=evidence,
        )


class RewriteModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.rewrite = dspy.Predict(RewriteAnswer)

    def __call__(self, answer, rewrite_instructions):
        return self.rewrite(
            answer=answer,
            rewrite_instructions=rewrite_instructions,
        )
