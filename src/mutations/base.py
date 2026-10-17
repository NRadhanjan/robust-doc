"""Base class for PDF structural mutations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union


class BaseMutation(ABC):
    """Abstract base class for controlled, non-adversarial PDF mutations."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def mutate(
        self,
        input_pdf_path: Union[str, Path],
        output_pdf_path: Union[str, Path],
        intensity: float = 1.0
    ) -> Path:
        """Applies mutation to input_pdf_path and saves to output_pdf_path.

        Args:
            input_pdf_path: Path to the original PDF.
            output_pdf_path: Destination path for the mutated PDF.
            intensity: Float between 0.0 and 1.0 representing perturbation severity.

        Returns:
            Path to the newly mutated PDF.
        """
        pass
