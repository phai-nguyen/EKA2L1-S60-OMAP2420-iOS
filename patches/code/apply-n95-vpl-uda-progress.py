#!/usr/bin/env python3
"""Report progress and honor cancellation while extracting VPL UDA/FAT data."""

from pathlib import Path
import sys


root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
source_path = root / "src/emu/system/src/installation/firmware.cpp"
source = source_path.read_text(encoding="utf-8")
marker = "N95VPL-UDA-PROGRESS1"

if marker in source:
    print("N95 UDA progress/cancellation patch already applied")
    raise SystemExit(0)

old_helpers = '''    static void extract_file(Fat::Image &img, Fat::Entry &entry, const std::string &path) {
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

                    extract_directory(img, baby, dir_path + common::ucs2_to_utf8(dir_name) + "\\\\");
                }
            }

            if ((mee.entry.file_attributes & (int)Fat::EntryAttribute::ARCHIVE) || (!(mee.entry.file_attributes & (int)Fat::EntryAttribute::DIRECTORY) && (mee.entry.file_size != 0))) {
                extract_file(img, mee, dir_path);
            }
        }
    }
'''

new_helpers = '''    // N95VPL-UDA-PROGRESS1: UDA/FAT extraction used to report only after the
    // whole tree finished and never polled cancel_cb. Report each 64 KiB chunk.
    static bool extract_file(Fat::Image &img, Fat::Entry &entry, const std::string &path,
        progress_changed_callback progress_cb, cancel_requested_callback cancel_cb,
        std::size_t &bytes_done, const std::size_t total_bytes) {
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
            if (cancel_cb && cancel_cb()) {
                return false;
            }

            std::uint32_t size_to_take = std::min<std::uint32_t>(CHUNK_SIZE, size_left);
            const std::uint32_t amount_read = img.read_from_cluster(
                &temp_buf[0], offset, entry.entry.starting_cluster, size_to_take);
            if (amount_read != size_to_take) {
                LOG_ERROR(SYSTEM, "Can't read {} bytes from UDA file {}",
                    size_to_take - amount_read, filename);
                return false;
            }

            size_left -= size_to_take;
            offset += size_to_take;

            f.write(reinterpret_cast<const char *>(&temp_buf[0]), size_to_take);
            bytes_done += size_to_take;

            if (progress_cb) {
                progress_cb(std::min(bytes_done, total_bytes), total_bytes);
            }
        }

        return true;
    }

    static bool extract_directory(Fat::Image &img, Fat::Entry mee, std::string dir_path,
        progress_changed_callback progress_cb, cancel_requested_callback cancel_cb,
        std::size_t &bytes_done, const std::size_t total_bytes) {
        common::create_directories(dir_path);

        while (img.get_next_entry(mee)) {
            if (cancel_cb && cancel_cb()) {
                return false;
            }

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

                    if (!extract_directory(img, baby, dir_path + common::ucs2_to_utf8(dir_name) + "\\\\",
                            progress_cb, cancel_cb, bytes_done, total_bytes)) {
                        return false;
                    }
                }
            }

            if ((mee.entry.file_attributes & (int)Fat::EntryAttribute::ARCHIVE) || (!(mee.entry.file_attributes & (int)Fat::EntryAttribute::DIRECTORY) && (mee.entry.file_size != 0))) {
                if (!extract_file(img, mee, dir_path, progress_cb, cancel_cb, bytes_done, total_bytes)) {
                    return false;
                }
            }
        }

        return true;
    }
'''

if old_helpers not in source:
    raise SystemExit("N95 UDA patch anchor not found in FAT extraction helpers")
source = source.replace(old_helpers, new_helpers, 1)

old_call = '''            Fat::Entry bootstrap_entry;
            extract_directory(fat_img, bootstrap_entry, fat_dump_base);

            if (progress_cb)
                progress_cb(1, 1);
'''
new_call = '''            Fat::Entry bootstrap_entry;
            std::size_t bytes_done = 0;
            const std::size_t total_bytes = std::max<std::size_t>(
                1, static_cast<std::size_t>(fat_image_file.size()));
            if (!extract_directory(fat_img, bootstrap_entry, fat_dump_base,
                    progress_cb, cancel_cb, bytes_done, total_bytes)) {
                if (cancel_cb && cancel_cb()) {
                    LOG_INFO(SYSTEM, "UDA firmware extraction cancelled");
                } else {
                    LOG_ERROR(SYSTEM, "UDA firmware extraction failed");
                }
                eka2l1::common::remove(image_path);
                return device_installation_general_failure;
            }

            if (progress_cb)
                progress_cb(1, 1);
'''

if old_call not in source:
    raise SystemExit("N95 UDA patch anchor not found at FAT extraction call")
source = source.replace(old_call, new_call, 1)

source_path.write_text(source, encoding="utf-8")
print("Applied N95 UDA progress/cancellation patch")
