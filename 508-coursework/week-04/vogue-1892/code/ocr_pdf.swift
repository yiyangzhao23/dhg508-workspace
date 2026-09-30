// Render each PDF page to an image and OCR it with Apple's Vision framework.
// The three 1892 Vogue issues are image-only scans (no text layer), so this is
// the first step of the pipeline: PDF -> page image -> OCR text.
//
// Build: swiftc -O -sdk /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk \
//          -target arm64-apple-macosx26.0 -o /tmp/ocr_pdf code/ocr_pdf.swift
// Run:   /tmp/ocr_pdf "sources/raw/Vogue - 1892-12-17.pdf" artifacts/pages/1892-12-17 2.0
//
// Usage: ocr_pdf <file.pdf> <outdir> [scale]
import Foundation
import PDFKit
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count >= 3 else {
    FileHandle.standardError.write("usage: ocr_pdf <file.pdf> <outdir> [scale]\n".data(using: .utf8)!)
    exit(1)
}
let pdfURL = URL(fileURLWithPath: args[1])
let outdir = args[2]
let scale: CGFloat = args.count >= 4 ? CGFloat(Double(args[3]) ?? 2.0) : 2.0

try? FileManager.default.createDirectory(atPath: outdir, withIntermediateDirectories: true)

guard let doc = PDFDocument(url: pdfURL) else {
    FileHandle.standardError.write("cannot open pdf\n".data(using: .utf8)!)
    exit(1)
}

print("PAGES \(doc.pageCount)")
for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { continue }
    let bounds = page.bounds(for: .mediaBox)
    let w = Int((bounds.width * scale).rounded())
    let h = Int((bounds.height * scale).rounded())
    guard let ctx = CGContext(
        data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
    ) else { continue }
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    ctx.saveGState()
    ctx.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: ctx)
    ctx.restoreGState()
    guard let cg = ctx.makeImage() else { continue }

    // page image (large; kept in artifacts, never committed)
    let imgPath = (outdir as NSString).appendingPathComponent(String(format: "page-%03d.jpg", i + 1))
    let rep = NSBitmapImageRep(cgImage: cg)
    if let data = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.82]) {
        try? data.write(to: URL(fileURLWithPath: imgPath))
    }

    // OCR, ordered top-to-bottom then left-to-right
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.recognitionLanguages = ["en-US"]
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    do { try handler.perform([request]) } catch {
        FileHandle.standardError.write("ocr failed page \(i + 1): \(error)\n".data(using: .utf8)!)
    }
    let observations = (request.results ?? []).sorted { a, b in
        // Vision boxes use a bottom-left origin; larger maxY is higher on the page.
        let ay = a.boundingBox.maxY, by = b.boundingBox.maxY
        if abs(ay - by) > 0.008 { return ay > by }
        return a.boundingBox.minX < b.boundingBox.minX
    }
    var lines: [String] = []
    for obs in observations {
        if let top = obs.topCandidates(1).first { lines.append(top.string) }
    }
    let txtPath = (outdir as NSString).appendingPathComponent(String(format: "page-%03d.txt", i + 1))
    try? (lines.joined(separator: "\n") + "\n").write(toFile: txtPath, atomically: true, encoding: .utf8)
    print("page \(i + 1)/\(doc.pageCount) chars=\(lines.joined().count)")
}
