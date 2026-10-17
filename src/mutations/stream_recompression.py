"""Mutation 2: Stream Recompression & Filter Adjustment."""

from pathlib import Path
from typing import Union
import pikepdf
from .base import BaseMutation


class StreamRecompressionMutation(BaseMutation):
    """Mutates stream compression and internal stream encodings.

    Simulates routine PDF 'Reduce File Size' optimizations, Ghostscript passes,
    or scanner recompression without altering functional payload semantics.
    """

    def __init__(self):
        super().__init__(name="recompression")

    def mutate(
        self,
        input_pdf_path: Union[str, Path],
        output_pdf_path: Union[str, Path],
        intensity: float = 1.0
    ) -> Path:
        input_pdf_path = Path(input_pdf_path)
        output_pdf_path = Path(output_pdf_path)
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        with pikepdf.open(input_pdf_path) as pdf:
            streams_count = 0
            for obj in pdf.objects:
                if isinstance(obj, pikepdf.Stream):
                    streams_count += 1

            # Based on intensity, alter stream compression
            modified = 0
            target_to_modify = max(1, int(streams_count * intensity))

            for obj in pdf.objects:
                if isinstance(obj, pikepdf.Stream):
                    try:
                        if intensity > 0.5:
                            # High intensity: decompress stream data or invert filter
                            if "/Filter" in obj:
                                obj.uncompress()
                        else:
                            # Lower intensity: ensure compression is enforced
                            obj.compress()
                        modified += 1
                        if modified >= target_to_modify:
                            break
                    except Exception:
                        continue

            # Save with controlled stream compression settings
            if intensity > 0.7:
                pdf.save(
                    output_pdf_path,
                    compress_streams=False,
                    object_stream_mode=pikepdf.ObjectStreamMode.disable
                )
            else:
                pdf.save(
                    output_pdf_path,
                    compress_streams=True,
                    object_stream_mode=pikepdf.ObjectStreamMode.generate
                )

        return output_pdf_path
