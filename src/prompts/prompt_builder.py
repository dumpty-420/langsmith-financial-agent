from typing import List
from abc import ABC, abstractmethod

class PromptComponent(ABC):
    @abstractmethod
    def render(self, context: dict) -> str:
        """Render the component as a string using the provided context."""
        pass

class PromptBuilder:
    """
    Builds optimized prompts by combining modular components.
    All data for components is provided via the context dictionary.
    """

    def __init__(self, components: List[PromptComponent], context: dict):
        """
        Initialize PromptBuilder with components and context.
        Args:
            components: List of PromptComponent instances.
            context: Dictionary containing data for components (e.g., id).
        """
        self.components = components
        self.context = context

    def build(self) -> str:
        """
        Build the final prompt by rendering and combining all components.
        Returns:
            Complete prompt string.
        """
        return "\n\n".join(component.render(self.context) for component in self.components)
