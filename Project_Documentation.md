# **Financial Document Analysis with GenAI**

## **1. Introduction**
Financial data extraction is a critical task in banking and finance, where accurate and structured information is needed for decision-making. This project focuses on automating the extraction of financial metrics from PDF documents using **GenAI**, allowing for structured tabular outputs and high-level financial summaries.

## **2. Objective**
The goal of this project is to:
- Extract key financial metrics (Revenue, Expenses, Net Income, etc.) from structured PDF financial reports.
- Process and store the extracted information in structured CSV formats (under `/data`).
- Generate an AI-powered financial summary report that provides insights into the company’s financial health.

## **3. Methodology & Thought Process**

Given the context of the problem I placed ideals these as important:
- We REALLY want to keep the right figures, so potentially trying lower end models for this, while it can be accurate a fair amount of the time, likely does not counteract the risk of it eventually hallucinating (comes in later for scaling strategies). 
- Not all LLMs are equal.



### **3.1 Extracting Text & Preprocessing Data**
#### **Thought Process:** 
I had initially done some basic research into whether this task had been solved before, and whether OCR tools, a pdf text extractor, or an LLM would be the best solution at hand (considering the accuracy points etc.).

After some reading I came across various OCR tools (AWS textract, marker) for extracting financial data from PDFs, and the open source `gmft` library had good reviews. (relies on Table transformers from Microsoft). Others had commercial usage agreements.

*However,* whilst GMFT has great metrics, with this pdf type it performed very poorly. After some research into its usage, gmft seems to be designed for actual tables in scientific journals (close together and compressed), whilst this pdf is **majority of white space, and tables often span multiple pages**, so it couldn't deal with this well.

**Sub-Tables:** I had considered whether to segment the tables into sub-tables (e.g Income statement has Revenues, Expenses, ...) but eventually decided against this as manually doing this would be somewhat time consuming (considering different name variations, caps lock differences like Table 3/4, ...) and if fed into a GenAI model, this would marginally increase the token size anyways and not yield any real benefit. Furthermore, opening the fully extracted table `.csv`'s in Excel gives a very human-readable view regardless.


#### **Final Approach:**
- **PDF Parsing**: Extract raw text using `pdfplumber`. Whilst noticeably slower than `pypdf2`, it had fewer missing characters, making it a better tradeoff when accuracy is important such as this use case. Ideally, a pdf should only be extracted once so this slow difference is not a large issue either.
- **Cleaning:** Removed headers, footers, and page numbers to ensure clean data (and less tokens for LLMs to consume)
- **Segmentation**: Used regex-based splitting to break down the document into individual financial statements as each main table was followed by the sentence `The above statement should be read in conjunction with the notes.`. (Income Statement, Balance Sheet, etc.). Initially, I considered simple .split() but opted for regex for better flexibility across different document formats.


### **Validation:**
 Validation (especially in the context of finances) is incredibly important. However, most of the methods I could think of were hard to achieve or required considerable time investment. E.g comparing automated strategies (LLMs vs coded extracted dataframes) could work, but in the event of a disagreement, which is correct? Manual intervention is likely necessary. In the end, my validation strategy was quite simple - validate all csv's are using floats (numbers, and not random 'O's instead of zeros, etc), and manually checking between csv and pdf for any issues/inaccuracies. More time spent on this is recommended, such as implementing sum checks to check if fields add up to the totals.



### 3.2 Financial Data Extraction Using GenAI

#### Thought Process:

- **Manual Parsing vs. AI-Based Extraction**: I initially experimented with writing custom regex and heuristics to extract structured data from tables. However, the variation in formatting (e.g., multi-line headers, inconsistent column alignment, different column names, ...) and especially considering future documents may have slightly different formats made this approach unsatisfactory. For instance, consider scaling - our regex assumes 3 column tables for instance. There may be other bugs and different kinds of multilined strings, or simply just malformatted docs. What then? This would require significant time and effort to come to solutions to, using a manual method.

- **GenAI Extraction**: Instead of writing hardcoded extraction logic which is hard to scale, I leveraged GenAI to extract structured JSON directly from text-based financial tables as these are much more flexible and easier to scale with.

#### Selecting The Correct GenAI Model

**Local Models:"** Since I wanted to test **local LLMs for privacy reasons**, I initially tried **DeepSeek-R1 (1.5B) running on an ollama serve**, but it **performed poorly**. Some issues:
- **Repeated values** appeared in extracted tables.
- **Hallucination** of financial figures, often using the Notes table instead.
- **Inconsistent markdown formatting** (e.g., misaligned tables).

A 1.5b model is much too small for tasks of this complexity and will output nonsencial values - I would recommend experimenting with at least a 70b model if pushing the local approach (which is easily doable with a cloud server for instance or a few GPUs).

**Online APIs**: 
Given these challenges, I switched to **Gemini 2.0 Flash API**, because:
- **Free-tier availability** (no cost concerns).
- **Large context window (1M tokens)** → Ensures **full financial statements fit into memory**.
- **Better Complexity threshold**: Much greater ability to comprehend and complete tasks with minimal hallucinations.

**Privacy concerns:** This is a concern but in this case, financial statements are often publicly disclosed documents and this specific instance is a sample assessment so it's fine.

If we had to use private documents, I would definitely recommend looking into setting up a 70b model locally or on cloud.


**Final Approach:**
1. **Sent each segmented table** to Gemini with a structured prompt.
2. **Extracted structured JSON** with:
   - `table_name` (e.g., "Income Statement").
   - `csv_data` (fully formatted financial table).
3. **Saved CSV files** for downstream processing.


### 3.3 Generating the Summary Report
**Thought Process**:
Since we had decided to use the Gemini API, this makes the report generation relatively easy as Gemini 2.0 Flash is a decent model that can do tasks of this complexity easily.

I experimented with different prompts and repeating the same prompts to see the level of variation; but overall the documents all repeated the same conclusions and stated the main key metrics (though there is some variation in the table metrics used - this can be clamped via changing the prompt).

#### **Final Approach:**
1. Read extracted CSVs from 3.2.
2. Sent them to Gemini 2.0 to generate a markdown-based financial summary.
3. Converted the markdown summary into a well-structured PDF report using `markdownpdf`.

### 3.4 Considering Scale
## Phase 5 - Scaling And Stuff

#### For scaling preprocessing

We currently use a mix of manual table names w/ regex patterns which is fine here, but in more varied datasets we may have some errors as people use slightly different words/terminology that falls through the regex patterns. So potentially using NLP based methods (like spacy, etc.) would help here. 


#### RAG:
Potential for RAG for greater reliability or some sort of pre-processed database so the PDF reading and processing doesn't have to happen every time. 
With RAG, you can retrieve more accurate answers while still being able to ask the GenAI model any query.

RAG is a trade-off of speed for accuracy, but for large databases, this is pretty practical because of context limits (i.e., you can’t throw 10,000 docs into the LLM, so use a retriever to find 5 relevant documents instead!).

### Other ideas:
- Deploying on cloud (AWS lambda) for better pipelines and scalability (e.g preprocessing function runs whenever new pdf is inputted, then thrown into a database)


## **4. Challenges & Solutions**

### **4.1 Extracting Tabular Data from PDFs**
**Challenge:** Financial statements often contain complex tabular structures, making data extraction non-trivial. Some tables contained **multi-line headers** (e.g., "Asset Revaluation Reserve"), which broke naive parsing approaches.

**Solution:** Used **regex-based pattern matching** and structured parsing methods. Considered a generalized function for all tables but opted for **segmented extraction** to ensure accuracy.

### **4.2 Handling Variations in Financial Statements**
**Challenge:** Different companies use different formats for their financial reports, making it difficult to build a one-size-fits-all parser.

**Solution:** Implemented **flexible regex patterns** and prompt engineering to allow for structured AI extraction across different document layouts. Manual table type classification was considered but ultimately deemed inefficient for scalability.

### **4.3 Ensuring Accuracy in AI-Extracted Data**
**Challenge:** GenAI may hallucinate or misinterpret some figures, particularly when handling **financial negative values** (e.g., bracketed losses `(123,000)` may not always be recognized as negative values).

**Solution:** Applied **post-processing validation**, ensuring extracted values match expected financial ranges and formats. The model was instructed explicitly to **preserve all negative signs** and format numbers correctly.

## **5. Results**
- **Extracted Financial Tables:** CSV files containing structured financial metrics.
- **AI-Generated Summary:** A PDF report summarizing revenue, expenses, and financial trends.
- **Scalability Considerations:** The pipeline was designed to allow **future expansion into a RAG-based system**, where preprocessed tables could be stored for retrieval and querying instead of rerunning extraction on every query.

## **6. Future Improvements**
- **Enhance data validation** by integrating a rule-based financial integrity check - such as implementing sum checks to check if fields add up to the totals.

- **Explore Local AI Models:** Investigated **deepseek-r1:1.5B** as a potential local alternative but noted that larger models (e.g., 70B) would be preferable for accuracy. **Privacy concerns** regarding API-based processing could be mitigated with a locally deployed high-parameter model.
- **Optimize Preprocessing for Large-Scale Processing:** Current preprocessing relies on regex for table names, but NLP-based classification (e.g., `spacy`) could improve robustness across varied datasets.

## **7. Conclusion**
This project successfully demonstrates how AI can be leveraged for financial data extraction and analysis. By automating the pipeline, we improve efficiency and accuracy in handling large-scale financial documents. Considerations for future scalability, including **cloud-based deployment** and **retrieval-augmented generation (RAG)**, offer opportunities to make financial data extraction even more robust and dynamic.


