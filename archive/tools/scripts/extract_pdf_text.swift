import Foundation
import PDFKit

if CommandLine.arguments.count < 2 {
    fputs("usage: extract_pdf_text <pdf-path>\n", stderr)
    exit(1)
}

let path = CommandLine.arguments[1]
guard let document = PDFDocument(url: URL(fileURLWithPath: path)) else {
    fputs("failed to open pdf\n", stderr)
    exit(2)
}

for index in 0..<document.pageCount {
    print("=== PAGE \(index + 1) ===")
    if let page = document.page(at: index), let text = page.string {
        print(text)
    }
}
