from langchain_community.document_loaders import Docx2txtLoader


def QAfile(doc_path="content/qa.docx"):
    loader = Docx2txtLoader(doc_path)
    return loader.load()