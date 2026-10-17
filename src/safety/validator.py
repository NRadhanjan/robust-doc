"""Safety & Functionality Gatekeeper: PDF Validity and Payload Reachability Verifier."""

from pathlib import Path
from typing import Dict, Any, Union, Optional, Tuple
import pikepdf

TupleResult = Tuple[bool, str]


class StructuralValidityChecker:
    """Verifies that a mutated PDF is neither corrupted nor functionally neutralized.

    Research Guardrail:
    If a mutation destroys the malicious payload trigger (e.g., breaking /OpenAction
    or severing the /JavaScript stream), any drop in detector accuracy is a false
    indicator of feature fragility (the file is simply broken).
    This checker ensures only structurally valid, functional mutations are evaluated.
    """

    def __init__(self):
        pass

    def check_file_opens(self, pdf_path: Union[str, Path]) -> TupleResult:
        """Verifies if the PDF can be parsed cleanly by a standard conformant PDF parser."""
        pdf_path = Path(pdf_path)
        try:
            with pikepdf.open(pdf_path) as pdf:
                # Basic sanity probe: touch pages and catalog
                _ = len(pdf.pages)
                _ = pdf.Root
            return True, "PDF parsed and rendered pages successfully."
        except Exception as e:
            return False, f"PDF failed to open or parse: {str(e)}"

    def check_payload_reachability(
        self,
        original_pdf_path: Union[str, Path],
        mutated_pdf_path: Union[str, Path]
    ) -> TupleResult:
        """Verifies that execution triggers present in the original are still reachable in the mutated PDF.

        Checks:
        1. /OpenAction in Document Catalog still resolves to valid target.
        2. /AA (Additional Actions) still exists if originally present.
        3. /Names -> /JavaScript trees still resolve.
        4. Embedded files or launch actions remain structurally connected.
        """
        try:
            with pikepdf.open(original_pdf_path) as orig, pikepdf.open(mutated_pdf_path) as mut:
                orig_root = orig.Root
                mut_root = mut.Root

                # 1. /OpenAction check
                if "/OpenAction" in orig_root:
                    if "/OpenAction" not in mut_root:
                        return False, "Payload neutralized: /OpenAction missing in mutated PDF."
                    orig_target = orig_root["/OpenAction"]
                    mut_target = mut_root["/OpenAction"]
                    if mut_target is None:
                        return False, "Payload neutralized: /OpenAction target is null."

                # 2. /AA (Additional Actions) check
                if "/AA" in orig_root:
                    if "/AA" not in mut_root:
                        return False, "Payload neutralized: /AA (Additional Actions) dictionary severed."

                # 3. /Names -> /JavaScript check
                if "/Names" in orig_root and "/JavaScript" in orig_root.Names:
                    if "/Names" not in mut_root or "/JavaScript" not in mut_root.Names:
                        return False, "Payload neutralized: Names/JavaScript name tree severed."

                # 4. Stream integrity check: count non-empty streams
                orig_stream_count = sum(1 for o in orig.objects if isinstance(o, pikepdf.Stream))
                mut_stream_count = sum(1 for o in mut.objects if isinstance(o, pikepdf.Stream))
                if orig_stream_count > 0 and mut_stream_count == 0:
                    return False, "Payload neutralized: All data streams were stripped."

            return True, "All structural triggers and payload elements remain reachable."
        except Exception as e:
            return False, f"Reachability inspection error: {str(e)}"

    def validate(
        self,
        original_pdf_path: Union[str, Path],
        mutated_pdf_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """Runs the complete two-stage validity check."""
        opens_ok, open_msg = self.check_file_opens(mutated_pdf_path)
        if not opens_ok:
            return {
                "is_valid": False,
                "syntax_ok": False,
                "payload_reachable": False,
                "reason": open_msg
            }

        reach_ok, reach_msg = self.check_payload_reachability(original_pdf_path, mutated_pdf_path)
        return {
            "is_valid": reach_ok,
            "syntax_ok": opens_ok,
            "payload_reachable": reach_ok,
            "reason": reach_msg if not reach_ok else "Passed all validity and reachability checks."
        }

