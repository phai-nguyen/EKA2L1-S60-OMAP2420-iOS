#!/usr/bin/env python3
"""Expose EKA2L1's existing VPL/FPSX installer in the iOS device importer."""

from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
app = root / "src/emu/ios/App"
bridge = root / "src/emu/ios/Bridge"


def replace(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    if old not in source:
        raise SystemExit(f"VPL import anchor missing: {path}: {old[:80]!r}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


swift = app / "ContentView.swift"
if "N95VPL-IMPORT1" in swift.read_text(encoding="utf-8"):
    print("N95 VPL import already applied")
    raise SystemExit(0)

replace(swift,
    "// Device-install Form, in two flavours the user picks between.",
    "// Device-install Form: ROM/RPKG, 7z archive, or VPL/FPSX firmware folder.")
replace(swift,
    "private enum PickTarget { case rom, rpkg, archive }",
    "private enum PickTarget { case rom, rpkg, archive, firmwareFolder, firmwareFiles }")
replace(swift,
    "        case archive\n    }\n\n    @State private var source: SourceKind",
    "        case archive\n        case firmware\n    }\n\n    @State private var source: SourceKind")
replace(swift,
    "    @State private var archive: PickedFile?\n",
    "    @State private var archive: PickedFile?\n"
    "    @State private var firmwareFolder: PickedFile?\n"
    "    @State private var firmwareFiles: [URL] = []\n"
    "    @State private var vplFiles: [URL] = []\n"
    "    @State private var selectedVPLIndex = 0\n"
    "    @State private var showingFirmwareInstallError = false\n")
replace(swift,
    "        // Both flavours run the same way: hold the security scope open across a",
    "        // Every source holds its security scope open across a")
replace(swift,
    '                        Text("import.source.archive").tag(SourceKind.archive)\n',
    '                        Text("import.source.archive").tag(SourceKind.archive)\n'
    '                        Text("import.source.firmware").tag(SourceKind.firmware)\n')
replace(swift,
    '''                    } else {
                        Button { pickTarget = .archive; showingImporter = true } label: {
                            fileRow(title: String(localized: "import.archiveFile"), value: archive?.name)
                        }
                    }
                } footer: {''',
    '''                    } else if source == .archive {
                        Button { pickTarget = .archive; showingImporter = true } label: {
                            fileRow(title: String(localized: "import.archiveFile"), value: archive?.name)
                        }
                    } else {
                        // N95VPL-IMPORT1: pick the containing folder so the security scope
                        // also covers the FPSX files referenced by the selected VPL.
                        Button { pickTarget = .firmwareFolder; showingImporter = true } label: {
                            fileRow(title: String(localized: "import.firmwareFolder"),
                                    value: firmwareFolder?.name)
                        }
                        Button { pickTarget = .firmwareFiles; showingImporter = true } label: {
                            fileRow(title: String(localized: "import.firmwareFiles"),
                                    value: firmwareFiles.isEmpty ? nil : String(firmwareFiles.count))
                        }
                        if !vplFiles.isEmpty {
                            Picker("import.firmwareVPL", selection: $selectedVPLIndex) {
                                ForEach(vplFiles.indices, id: \\.self) { index in
                                    Text(vplFiles[index].lastPathComponent).tag(index)
                                }
                            }
                        }
                    }
                } footer: {''')
replace(swift,
    '''                    } else {
                        Text("import.archiveHint")
                    }
                }

                if let errorMessage''',
    '''                    } else if source == .archive {
                        Text("import.archiveHint")
                    } else {
                        Text("import.firmwareHint")
                    }
                }

                if let errorMessage''')
replace(swift,
    '                        .disabled(source == .looseFiles ? (rom == nil) : (archive == nil))',
    '                        .disabled(source == .looseFiles ? (rom == nil) :\n'
    '                                  source == .archive ? (archive == nil) : vplFiles.isEmpty)')
replace(swift,
    '''                          allowsMultipleSelection: false) { result in
                pick(result, target: pickTarget)''',
    '''                          allowsMultipleSelection: pickTarget == .firmwareFiles) { result in
                pick(result, target: pickTarget)''')
replace(swift,
    '''            .interactiveDismissDisabled(installing)
        }
    }

    private func fileRow''',
    '''            .interactiveDismissDisabled(installing)
            .alert("common.error", isPresented: $showingFirmwareInstallError) {
                Button("common.ok", role: .cancel) { showingFirmwareInstallError = false }
            } message: {
                Text(errorMessage ?? String(localized: "common.error"))
            }
        }
    }

    private func fileRow''')
replace(swift,
    '        case .archive: return archiveTypes\n',
    '        case .archive: return archiveTypes\n'
    '        case .firmwareFolder: return [.folder]\n'
    '        case .firmwareFiles: return [.data]\n')
replace(swift,
    '        case .archive: return "7z"\n',
    '        case .archive: return "7z"\n'
    '        case .firmwareFolder: return ""\n'
    '        case .firmwareFiles: return ""\n')
replace(swift,
    '''        guard case .success(let urls) = result, let url = urls.first else { return }
        let kind = expectedExtension(for: target)''',
    '''        guard case .success(let urls) = result, let url = urls.first else { return }
        if target == .firmwareFiles {
            let names = urls.map(\\.lastPathComponent)
            guard Set(names.map { $0.lowercased() }).count == names.count else {
                errorMessage = String(localized: "import.error.duplicateFirmwareFile")
                return
            }
            let candidates = urls.filter {
                $0.pathExtension.caseInsensitiveCompare("vpl") == .orderedSame
            }.sorted { $0.lastPathComponent.localizedStandardCompare($1.lastPathComponent) == .orderedAscending }
            guard !candidates.isEmpty else {
                errorMessage = String(localized: "import.error.noVPL")
                return
            }
            firmwareFolder = nil
            firmwareFiles = urls
            vplFiles = candidates
            selectedVPLIndex = 0
            errorMessage = nil
            return
        }
        if target == .firmwareFolder {
            let scoped = url.startAccessingSecurityScopedResource()
            defer { if scoped { url.stopAccessingSecurityScopedResource() } }
            do {
                let files = try FileManager.default.contentsOfDirectory(at: url,
                    includingPropertiesForKeys: [.isRegularFileKey], options: [.skipsHiddenFiles])
                let candidates = files.filter { file in
                    file.pathExtension.caseInsensitiveCompare("vpl") == .orderedSame &&
                    ((try? file.resourceValues(forKeys: [.isRegularFileKey]).isRegularFile) == true)
                }.sorted { $0.lastPathComponent.localizedStandardCompare($1.lastPathComponent) == .orderedAscending }
                guard !candidates.isEmpty else {
                    errorMessage = String(localized: "import.error.noVPL")
                    firmwareFolder = nil
                    vplFiles = []
                    return
                }
                firmwareFolder = PickedFile(name: url.lastPathComponent, url: url)
                firmwareFiles = []
                vplFiles = candidates
                selectedVPLIndex = 0
                errorMessage = nil
            } catch {
                firmwareFolder = nil
                vplFiles = []
                errorMessage = String(localized: "import.error.firmwareFolder")
            }
            return
        }
        let kind = expectedExtension(for: target)''')
replace(swift,
    '        case .archive: archive = picked\n',
    '        case .archive: archive = picked\n'
    '        case .firmwareFolder, .firmwareFiles: break\n')
replace(swift,
    '''        case .archive:
            guard let archive else { return }
            let archivePath = archive.url.path
            urls = [archive.url]
            run = { progress, cancel in
                EKA2L1Bridge.installDevice(archivePath: archivePath, progress: progress, cancelCheck: cancel)
            }
        }
''',
    '''        case .archive:
            guard let archive else { return }
            let archivePath = archive.url.path
            urls = [archive.url]
            run = { progress, cancel in
                EKA2L1Bridge.installDevice(archivePath: archivePath, progress: progress, cancelCheck: cancel)
            }

        case .firmware:
            guard vplFiles.indices.contains(selectedVPLIndex) else {
                errorMessage = String(localized: "import.error.noVPL")
                showingFirmwareInstallError = true
                return
            }
            let vplName = vplFiles[selectedVPLIndex].lastPathComponent
            if let firmwareFolder {
                let vplPath = vplFiles[selectedVPLIndex].path
                urls = [firmwareFolder.url]
                run = { progress, cancel in
                    EKA2L1Bridge.installDevice(vplPath: vplPath, progress: progress, cancelCheck: cancel)
                }
            } else {
                let files = firmwareFiles
                guard !files.isEmpty else {
                    errorMessage = String(localized: "import.error.noVPL")
                    showingFirmwareInstallError = true
                    return
                }
                urls = files
                run = { progress, cancel in
                    let manager = FileManager.default
                    let staged = manager.temporaryDirectory.appendingPathComponent(
                        "n95-vpl-" + UUID().uuidString, isDirectory: true)
                    do {
                        try manager.createDirectory(at: staged, withIntermediateDirectories: true)
                        defer { try? manager.removeItem(at: staged) }
                        for (index, file) in files.enumerated() {
                            if cancel() { return .cancelled }
                            try manager.copyItem(at: file, to: staged.appendingPathComponent(file.lastPathComponent))
                            progress(0.1 * Double(index + 1) / Double(files.count))
                        }
                        if cancel() { return .cancelled }
                        return EKA2L1Bridge.installDevice(
                            vplPath: staged.appendingPathComponent(vplName).path,
                            progress: { progress(0.1 + 0.9 * $0) }, cancelCheck: cancel)
                    } catch {
                        return .generalFailure
                    }
                }
            }
        }
''')
replace(swift,
    '                    errorMessage = installMessage(for: result)\n',
    '                    errorMessage = installMessage(for: result)\n'
    '                    showingFirmwareInstallError = source == .firmware\n')

swift_bridge = app / "EKA2L1Bridge.swift"
replace(swift_bridge,
    '    nonisolated static func bootDevice(at index: Int) -> Bool {',
    '''    // The caller keeps the containing folder security-scoped or stages all
    // selected sibling files while the core reads the VPL and its FPSX files.
    nonisolated static func installDevice(vplPath: String,
                                          progress: (@Sendable (Double) -> Void)? = nil,
                                          cancelCheck: (@Sendable () -> Bool)? = nil) -> EKA2L1InstallResult {
        EKA2L1Emulator.shared().installDevice(vplPath: vplPath,
                                              progress: progress, cancelCheck: cancelCheck)
    }

    nonisolated static func bootDevice(at index: Int) -> Bool {''')

header = bridge / "IosEmulator.h"
replace(header,
    '// Boot a previously-installed device by index:',
    '''// Install the first variant from a VPL description and adjacent FPSX files.
// The caller must hold a security scope on the containing directory until this
// synchronous call returns. Like the other installers, it does not boot.
- (EKA2L1InstallResult)installDeviceWithVplPath:(NSString *)vplPath
                                       progress:(nullable void (^)(double fraction))progress
                                    cancelCheck:(nullable BOOL (^)(void))cancelCheck
    NS_SWIFT_NAME(installDevice(vplPath:progress:cancelCheck:));

// Boot a previously-installed device by index:''')

objc = bridge / "IosEmulator.mm"
replace(objc,
    "// Shared body of the two install entry points below.",
    "// Shared body of the device install entry points below.")
replace(objc,
    '- (BOOL)bootDeviceAtIndex:(NSUInteger)index {',
    '''- (EKA2L1InstallResult)installDeviceWithVplPath:(NSString *)vplPath
                                       progress:(void (^)(double))progress
                                    cancelCheck:(BOOL (^)(void))cancelCheck {
    if (![NSFileManager.defaultManager fileExistsAtPath:vplPath]) {
        return EKA2L1InstallResultNotExist;
    }

    const std::string vpl_std = vplPath.UTF8String;
    const std::string storage = _state ? _state->conf.storage : std::string();
    const std::string root_c_path = eka2l1::add_path(storage, "drives/c/");
    const std::string root_e_path = eka2l1::add_path(storage, "drives/e/");

    return [self runDeviceInstall:^(eka2l1::device_manager *dvc, const std::string &rom_resident_path,
                                     const std::string &root_z_path, progress_changed_callback progress_cb,
                                     cancel_requested_callback cancel_cb) {
        return eka2l1::install_firmware(dvc, vpl_std, root_c_path, root_e_path,
            root_z_path, rom_resident_path,
            [](const std::vector<std::string> &variants) -> int { return 0; },
            progress_cb, cancel_cb);
    } progress:progress cancelCheck:cancelCheck];
}

- (BOOL)bootDeviceAtIndex:(NSUInteger)index {''')

print("Applied N95 VPL import")
