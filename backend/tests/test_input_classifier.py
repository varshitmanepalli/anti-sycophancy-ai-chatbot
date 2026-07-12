"""InputClassifier unit tests."""

import pytest

from app.config.settings import Settings
from app.domain.classification import InputCategory
from app.services.classification.classifier import InputClassifier
from app.services.classification.rule_based import RuleBasedClassifier


@pytest.fixture
def rule_classifier() -> RuleBasedClassifier:
    return RuleBasedClassifier()


@pytest.fixture
def input_classifier() -> InputClassifier:
    return InputClassifier(settings=Settings(classifier_mode="rules"))


class TestRuleBasedClassifier:
    def test_classify_fact(self, rule_classifier: RuleBasedClassifier):
        result = rule_classifier.classify("What is the capital of France?")
        assert result.category == InputCategory.FACT
        assert result.confidence > 0.3
        assert result.method == "rules"

    def test_classify_opinion(self, rule_classifier: RuleBasedClassifier):
        result = rule_classifier.classify("Do you think Python is better than Java?")
        assert result.category == InputCategory.OPINION
        assert result.confidence > 0.2

    def test_classify_prediction(self, rule_classifier: RuleBasedClassifier):
        result = rule_classifier.classify("Will AI replace programmers by 2030?")
        assert result.category == InputCategory.PREDICTION
        assert result.confidence > 0.2

    def test_classify_programming(self, rule_classifier: RuleBasedClassifier):
        result = rule_classifier.classify(
            "How do I fix this Python bug in my FastAPI endpoint?"
        )
        assert result.category == InputCategory.PROGRAMMING
        assert result.confidence > 0.2

    def test_classify_relationship(self, rule_classifier: RuleBasedClassifier):
        result = rule_classifier.classify(
            "Should I break up with my boyfriend? We've been arguing a lot."
        )
        assert result.category == InputCategory.RELATIONSHIP
        assert result.confidence > 0.2

    def test_classify_medical(self, rule_classifier: RuleBasedClassifier):
        result = rule_classifier.classify(
            "I have a fever and cough for 3 days — should I see a doctor?"
        )
        assert result.category == InputCategory.MEDICAL
        assert result.confidence > 0.2

    def test_classify_business(self, rule_classifier: RuleBasedClassifier):
        result = rule_classifier.classify(
            "How should I price my SaaS product to maximize revenue?"
        )
        assert result.category == InputCategory.BUSINESS
        assert result.confidence > 0.2

    def test_classify_politics(self, rule_classifier: RuleBasedClassifier):
        result = rule_classifier.classify(
            "Who will win the next presidential election?"
        )
        assert result.category in (InputCategory.POLITICS, InputCategory.PREDICTION)
        assert result.confidence > 0.1

    def test_classify_emotion(self, rule_classifier: RuleBasedClassifier):
        result = rule_classifier.classify(
            "I feel overwhelmed and anxious about everything lately."
        )
        assert result.category == InputCategory.EMOTION
        assert result.confidence > 0.2

    def test_classify_math(self, rule_classifier: RuleBasedClassifier):
        result = rule_classifier.classify("Calculate 15% of 240")
        assert result.category == InputCategory.MATH
        assert result.confidence > 0.2

    def test_classify_general_chat(self, rule_classifier: RuleBasedClassifier):
        result = rule_classifier.classify("Hello!")
        assert result.category == InputCategory.GENERAL_CHAT
        assert result.confidence > 0.2

    def test_scores_sum_approx_one(self, rule_classifier: RuleBasedClassifier):
        result = rule_classifier.classify("What is the speed of light?")
        total = sum(result.scores.values())
        assert 0.99 <= total <= 1.01

    def test_all_categories_in_scores(self, rule_classifier: RuleBasedClassifier):
        result = rule_classifier.classify("Tell me something interesting.")
        assert len(result.scores) == len(InputCategory)


class TestInputClassifier:
    @pytest.mark.asyncio
    async def test_rules_mode(self, input_classifier: InputClassifier):
        result = await input_classifier.classify("How do I write a recursive function?")
        assert result.category == InputCategory.PROGRAMMING
        assert 0.0 <= result.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_to_dict(self, input_classifier: InputClassifier):
        result = await input_classifier.classify("Hello there")
        data = result.to_dict()
        assert "category" in data
        assert "confidence" in data
        assert "scores" in data
