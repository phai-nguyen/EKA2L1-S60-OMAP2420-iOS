#!/usr/bin/env python3
"""Keep ROM-resident files intact while importing an N95 ROFx volume."""

from pathlib import Path
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
source_path = root / "src/emu/loader/src/rofs.cpp"
source = source_path.read_text(encoding="utf-8")
marker = "N95ROFS-EXTLINK1"

if marker in source:
    print("N95 ROFS external-reference fix already applied")
    raise SystemExit(0)

old = """        fname = add_path(base, fname);
        std::ofstream extract_stream(fname, std::ios_base::binary);

        const std::uint64_t org_pos = stream.tell();
        stream.seek(entry.file_addr_ - file_offset, common::seek_where::beg);
"""
new = """        // N95ROFS-EXTLINK1: ROFx entries may refer to a file already supplied
        // by the core ROM image. Such addresses precede this volume's file base;
        // leave the ROM copy untouched instead of seeking with unsigned underflow.
        const std::int64_t relative_file_addr = static_cast<std::int64_t>(entry.file_addr_)
            - static_cast<std::int64_t>(file_offset);
        if (relative_file_addr < 0) {
            return true;
        }

        const std::uint64_t file_pos = static_cast<std::uint64_t>(relative_file_addr);
        const std::uint64_t image_size = stream.size();
        if ((file_pos > image_size) || (entry.file_size_ > image_size - file_pos)) {
            LOG_ERROR(LOADER,
                "ROFS file {} points outside its image (addr=0x{:08X}, size=0x{:08X})",
                common::ucs2_to_utf8(entry.filename_), entry.file_addr_, entry.file_size_);
            return false;
        }

        fname = add_path(base, fname);
        std::ofstream extract_stream(fname, std::ios_base::binary);
        if (!extract_stream) {
            LOG_ERROR(LOADER, "Can't create extracted ROFS file: {}", fname);
            return false;
        }

        const std::uint64_t org_pos = stream.tell();
        stream.seek(file_pos, common::seek_where::beg);
"""
if old not in source:
    raise SystemExit("N95 ROFS fix anchor not found in extract_file")
source = source.replace(old, new, 1)

old_read = """            if (amount_read < size_to_take) {
                LOG_WARN(LOADER, "Can't read {} bytes, skipping", size_to_take - amount_read);
            }
"""
new_read = """            if (amount_read < size_to_take) {
                LOG_ERROR(LOADER, "Can't read {} bytes from ROFS file {}",
                    size_to_take - amount_read, common::ucs2_to_utf8(entry.filename_));
                return false;
            }
"""
if old_read not in source:
    raise SystemExit("N95 ROFS fix anchor not found in short-read handling")
source = source.replace(old_read, new_read, 1)

old_write = """            extract_stream.write(buf.data(), size_to_take);
            size_left -= size_to_take;
"""
new_write = """            extract_stream.write(buf.data(), size_to_take);
            if (!extract_stream) {
                LOG_ERROR(LOADER, "Can't write extracted ROFS file: {}", fname);
                return false;
            }
            size_left -= size_to_take;
"""
if old_write not in source:
    raise SystemExit("N95 ROFS fix anchor not found in file write handling")
source = source.replace(old_write, new_write, 1)

old_call = """                if (!extract_file(stream, file_entry, base, file_offset, progress_cb, cancel_cb, max_pos)) {
                    LOG_ERROR(LOADER, "Fail to extract file with name: {}", common::ucs2_to_utf8(file_entry.filename_));
                }
"""
new_call = """                if (!extract_file(stream, file_entry, base, file_offset, progress_cb, cancel_cb, max_pos)) {
                    LOG_ERROR(LOADER, "Fail to extract file with name: {}", common::ucs2_to_utf8(file_entry.filename_));
                    return false;
                }
"""
if old_call not in source:
    raise SystemExit("N95 ROFS fix anchor not found in directory extraction")
source = source.replace(old_call, new_call, 1)

source_path.write_text(source, encoding="utf-8")
print("Applied N95 ROFS external-reference fix")
