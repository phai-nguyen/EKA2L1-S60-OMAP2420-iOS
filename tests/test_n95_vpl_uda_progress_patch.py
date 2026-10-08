#!/usr/bin/env python3
"""Regression test for UDA/FAT progress and cancellation patch."""

from pathlib import Path
import subprocess
import sys
import tempfile


PATCH = Path(__file__).with_name("apply-n95-vpl-uda-progress.py")
OLD = r'''    static void extract_file(Fat::Image &img, Fat::Entry &entry, const std::string &path) {
        const std::u16string filename_16 = entry.get_filename();
        std::string filename = eka2l1::add_path(path, common::ucs2_to_utf8(filename_16));

        if (common::is_platform_case_sensitive()) {
            filename = common::lowercase_string(filename);
        }

        common::wo_std_file_stream f(filename, true);

        static constexpr std::uint32_t CHUNK_SIZE = 0x10000;

        std::vector<std::uint8_t> temp_buf;
        temp_buf.resize(CHUNK_SIZE);

        std::uint32_t size_left = entry.entry.file_size;
        std::uint32_t offset = 0;

        while (size_left != 0) {
            std::uint32_t size_to_take = std::min<std::uint32_t>(CHUNK_SIZE, size_left);
            if (img.read_from_cluster(&temp_buf[0], offset, entry.entry.starting_cluster, size_to_take) != size_to_take) {
                break;
            }

            size_left -= size_to_take;
            offset += size_to_take;

            f.write(reinterpret_cast<const char *>(&temp_buf[0]), size_to_take);
        }
    }

    static void extract_directory(Fat::Image &img, Fat::Entry mee, std::string dir_path) {
        common::create_directories(dir_path);

        while (img.get_next_entry(mee)) {
            if (mee.entry.file_attributes & (int)Fat::EntryAttribute::DIRECTORY) {
                // Also check if it's not the back folder (. and ..)
                // This can be done by gathering the name
                if (mee.entry.get_entry_type_from_filename() != Fat::EntryType::DIRECTORY) {
                    Fat::Entry baby;
                    if (!img.get_first_entry_dir(mee, baby))
                        break;

                    auto dir_name = mee.get_filename();

                    if (common::is_platform_case_sensitive()) {
                        dir_name = common::lowercase_ucs2_string(dir_name);
                    }

                    extract_directory(img, baby, dir_path + common::ucs2_to_utf8(dir_name) + "\\");
                }
            }

            if ((mee.entry.file_attributes & (int)Fat::EntryAttribute::ARCHIVE) || (!(mee.entry.file_attributes & (int)Fat::EntryAttribute::DIRECTORY) && (mee.entry.file_size != 0))) {
                extract_file(img, mee, dir_path);
            }
        }
    }
'''

with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    source = root / "src/emu/system/src/installation/firmware.cpp"
    source.parent.mkdir(parents=True)
    source.write_text(OLD + '''            Fat::Entry bootstrap_entry;
            extract_directory(fat_img, bootstrap_entry, fat_dump_base);

            if (progress_cb)
                progress_cb(1, 1);
''', encoding="utf-8")

    subprocess.run([sys.executable, str(PATCH), str(root)], check=True, capture_output=True, text=True)
    patched = source.read_text(encoding="utf-8")

    assert "N95VPL-UDA-PROGRESS1" in patched
    assert "cancel_cb && cancel_cb()" in patched
    assert "progress_cb(std::min(bytes_done, total_bytes), total_bytes)" in patched
    assert "extract_directory(img, baby" in patched and "progress_cb, cancel_cb" in patched
    assert "!extract_directory(fat_img" in patched
    assert "device_installation_general_failure" in patched

    subprocess.run([sys.executable, str(PATCH), str(root)], check=True, capture_output=True, text=True)
    assert source.read_text(encoding="utf-8") == patched

print("N95 UDA progress/cancellation patch regression check passed")
