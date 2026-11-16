// Render each PDF page to PNG for visual checks (macOS, uses PDFKit).
// Usage: swift raster.swift input.pdf outDir [scale]
import PDFKit
import AppKit

let args = CommandLine.arguments
guard args.count >= 3, let doc = PDFDocument(url: URL(fileURLWithPath: args[1])) else {
  print("usage: swift raster.swift input.pdf outDir [scale]"); exit(1)
}
let outDir = args[2]
let scale: CGFloat = args.count > 3 ? CGFloat(Double(args[3]) ?? 1.0) : 1.0
for i in 0..<doc.pageCount {
  let page = doc.page(at: i)!
  let r = page.bounds(for: .mediaBox)
  let img = NSImage(size: NSSize(width: r.width * scale, height: r.height * scale))
  img.lockFocus()
  NSColor.white.set(); NSRect(origin: .zero, size: img.size).fill()
  let ctx = NSGraphicsContext.current!.cgContext
  ctx.scaleBy(x: scale, y: scale)
  page.draw(with: .mediaBox, to: ctx)
  img.unlockFocus()
  let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
  try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: "\(outDir)/p\(String(format: "%02d", i + 1)).png"))
}
print(doc.pageCount)
