#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
log_cpp = root / "src/emu/common/src/log.cpp"

text = log_cpp.read_text(encoding="utf-8")

if "N95OMAP-LOGPACK1" in text:
    print("N95 OMAP2420 LOGPACK1 already applied")
    raise SystemExit(0)

old_ctor = '''        class capped_file_sink final : public spdlog::sinks::base_sink<std::mutex> {
        public:
            capped_file_sink(const std::string &filename, const std::size_t max_lines)
                : filename_(filename)
                , max_lines_(max_lines) {
                file_.open(filename_, true);
            }
'''

new_ctor = '''        class capped_file_sink final : public spdlog::sinks::base_sink<std::mutex> {
        public:
            capped_file_sink(const std::string &filename, const std::size_t max_lines, const bool truncate = true)
                : filename_(filename)
                , max_lines_(max_lines) {
                if (!truncate) {
                    std::ifstream source(filename_, std::ios::binary);
                    std::string line;
                    while (std::getline(source, line)) {
                        ++lines_;
                    }
                }

                file_.open(filename_, truncate);

                if (!truncate && (lines_ >= max_lines_)) {
                    drop_oldest_lines();
                }
            }
'''

if old_ctor not in text:
    raise SystemExit("LOGPACK1: capped_file_sink constructor anchor not found")
text = text.replace(old_ctor, new_ctor, 1)

old_factory = '''        std::shared_ptr<spdlog::sinks::sink> make_capped_file_sink(const std::string &filename, const std::size_t max_lines) {
            return std::make_shared<capped_file_sink>(filename, max_lines);
        }
'''

new_factory = '''        std::shared_ptr<spdlog::sinks::sink> make_capped_file_sink(const std::string &filename, const std::size_t max_lines) {
            return std::make_shared<capped_file_sink>(filename, max_lines, true);
        }

        static std::shared_ptr<spdlog::sinks::sink> make_capped_append_file_sink(
            const std::string &filename, const std::size_t max_lines) {
            return std::make_shared<capped_file_sink>(filename, max_lines, false);
        }
'''

if old_factory not in text:
    raise SystemExit("LOGPACK1: capped sink factory anchor not found")
text = text.replace(old_factory, new_factory, 1)

old_setup_head = '''        void setup_log(std::shared_ptr<base_logger> gui_logger) {
            const char *log_file_name = "EKA2L1.log";
            const char *log_file_name_prev = "EKA2L1_TakeThis.log";

            if (common::exists(log_file_name)) {
                common::move_file(log_file_name, log_file_name_prev);
            }
'''

new_setup_head = '''        void setup_log(std::shared_ptr<base_logger> gui_logger) {
            const char *log_file_name = "EKA2L1.log";
            const char *log_file_name_prev = "EKA2L1_TakeThis.log";

#if EKA2L1_PLATFORM(IOS)
            // N95OMAP-LOGPACK1
            // Keep the familiar four-file diagnostic set used by the device-test
            // builds. EKA2L1_Persistent.log is append-only across launches but uses
            // the same line cap as the normal log; Persistent-prev is a snapshot
            // taken before this launch starts writing.
            const char *log_file_name_persistent = "EKA2L1_Persistent.log";
            const char *log_file_name_persistent_prev = "EKA2L1_Persistent-prev.log";

            if (common::exists(log_file_name_persistent)) {
                common::copy_file(log_file_name_persistent, log_file_name_persistent_prev, true);
            }
#endif

            if (common::exists(log_file_name)) {
                common::move_file(log_file_name, log_file_name_prev);
            }
'''

if old_setup_head not in text:
    raise SystemExit("LOGPACK1: setup_log header anchor not found")
text = text.replace(old_setup_head, new_setup_head, 1)

old_sinks = '''            sinks.push_back(color_dist_sink);
            sinks.push_back(make_capped_file_sink(log_file_name, LOG_FILE_MAX_LINES));

#ifdef _MSC_VER
'''

new_sinks = '''            sinks.push_back(color_dist_sink);
            sinks.push_back(make_capped_file_sink(log_file_name, LOG_FILE_MAX_LINES));

#if EKA2L1_PLATFORM(IOS)
            sinks.push_back(make_capped_append_file_sink(log_file_name_persistent, LOG_FILE_MAX_LINES));
#endif

#ifdef _MSC_VER
'''

if old_sinks not in text:
    raise SystemExit("LOGPACK1: sink insertion anchor not found")
text = text.replace(old_sinks, new_sinks, 1)

log_cpp.write_text(text, encoding="utf-8")
print("Applied N95 OMAP2420 LOGPACK1")
