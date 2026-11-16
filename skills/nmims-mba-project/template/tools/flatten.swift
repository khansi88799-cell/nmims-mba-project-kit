// Flatten a PNG onto white and report corner/edge pixel colours. Usage: swift flatten.swift in.png out.png
import AppKit
let a = CommandLine.arguments
let img = NSImage(contentsOfFile: a[1])!
let rep0 = NSBitmapImageRep(data: img.tiffRepresentation!)!
for (x,y) in [(0,0),(5,5),(20,20),(2,166),(423,166)] { if let c = rep0.colorAt(x: x, y: y) { print("px",x,y, c.redComponent, c.greenComponent, c.blueComponent, c.alphaComponent) } }
let w = rep0.pixelsWide, h = rep0.pixelsHigh
let out = NSImage(size: NSSize(width: w, height: h))
out.lockFocus(); NSColor.white.set(); NSRect(x: 0, y: 0, width: w, height: h).fill()
img.draw(in: NSRect(x: 0, y: 0, width: w, height: h)); out.unlockFocus()
let rep = NSBitmapImageRep(data: out.tiffRepresentation!)!
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[2]))
