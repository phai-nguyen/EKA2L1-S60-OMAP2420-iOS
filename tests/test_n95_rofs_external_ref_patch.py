#!/usr/bin/env python3
"""Regression check that the N95 ROFS guard applies to the pinned parser."""

from pathlib import Path
import subprocess
import sys
import tempfile


PATCH = Path(__file__).resolve().parents[1] / "patches/code/apply-n95-rofs-external-ref-fix.py"

with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    parser = root / "src/emu/loader/src/rofs.cpp"
    parser.parent.mkdir(parents=True)
    parser.write_text(
        """        fname = add_path(base, fname);
        std::ofstream extract_stream(fname, std::ios_base::binary);

        const std::uint64_t org_pos = stream.tell();
        stream.seek(entry.file_addr_ - file_offset, common::seek_where::beg);
            if (amount_read < size_to_take) {
                LOG_WARN(LOADER, \"Can't read {} bytes, skipping\", size_to_take - amount_read);
            }
            extract_stream.write(buf.data(), size_to_take);
            size_left -= size_to_take;
                if (!extract_file(stream, file_entry, base, file_offset, progress_cb, cancel_cb, max_pos)) {
                    LOG_ERROR(LOADER, \"Fail to extract file with name: {}\", common::ucs2_to_utf8(file_entry.filename_));
                }
""",
        encoding="utf-8",
    )

    subprocess.run([sys.executable, str(PATCH), str(root)], check=True, capture_output=True, text=True)
    patched = parser.read_text(encoding="utf-8")

    assert "N95ROFS-EXTLINK1" in patched
    assert patched.index("relative_file_addr < 0") < patched.index("std::ofstream extract_stream")
    assert "entry.file_size_ > image_size - file_pos" in patched
    assert "Can't read {} bytes from ROFS file {}" in patched
    assert "return false;\n                }" in patched

    # Reapplying the workflow patch must be safe and leave the transformed file intact.
    subprocess.run([sys.executable, str(PATCH), str(root)], check=True, capture_output=True, text=True)
    assert parser.read_text(encoding="utf-8") == patched

print("N95 ROFS external-reference patch regression check passed")
