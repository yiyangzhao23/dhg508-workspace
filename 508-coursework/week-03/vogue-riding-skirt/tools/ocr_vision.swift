// Machine OCR with Apple's Vision framework.
// Build:  swiftc -O -o /tmp/ocr_vision tools/ocr_vision.swift
// Run:    /tmp/ocr_vision pages/vogue-p48.jpg > pages/raw-ocr-p48.txt
import Foundation
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count >= 2 else {
    FileHandle.standardError.write("usage: ocr_vision <image>\n".data(using: .utf8)!)
    exit(1)
}
let url = URL(fileURLWithPath: args[1])
guard let image = NSImage(contentsOf: url),
      let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    FileHandle.standardError.write("cannot load image\n".data(using: .utf8)!)
    exit(1)
}

let request = VNRecognizeTextRequest { req, _ in
    guard let observations = req.results as? [VNRecognizedTextObservation] else { return }
    for obs in observations {
        if let top = obs.topCandidates(1).first {
            print(top.string)
        }
    }
}
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(cgImage: cg, options: [:])
do {
    try handler.perform([request])
} catch {
    FileHandle.standardError.write("ocr failed: \(error)\n".data(using: .utf8)!)
    exit(1)
}
