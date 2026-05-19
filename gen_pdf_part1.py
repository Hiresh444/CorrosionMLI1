from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_fill_color(30, 60, 114)
        self.rect(0, 0, 210, 18, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 11)
        self.set_xy(0, 4)
        self.cell(0, 10, 'Corrosion Rate Prediction - ML Study Guide', align='C')
        self.set_text_color(0, 0, 0)
        self.ln(14)

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def section(self, title):
        self.ln(4)
        self.set_fill_color(30, 60, 114)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 9, f'  {title}', fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def subsection(self, title):
        self.ln(2)
        self.set_fill_color(200, 220, 255)
        self.set_text_color(20, 40, 100)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 7, f'  {title}', fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def body(self, text):
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 6, text)
        self.ln(1)

    def bullet(self, items):
        self.set_font('Helvetica', '', 10)
        for item in items:
            self.cell(8)
            self.multi_cell(0, 6, f'* {item}')

    def qa(self, q, a):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(180, 60, 0)
        self.multi_cell(0, 6, f'Q: {q}')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 80, 0)
        self.multi_cell(0, 6, f'A: {a}')
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def code_box(self, code):
        self.set_fill_color(240, 240, 240)
        self.set_font('Courier', '', 8)
        self.multi_cell(0, 5, code, fill=True)
        self.set_font('Helvetica', '', 10)
        self.ln(1)

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_margins(15, 22, 15)

# ── COVER PAGE ──
pdf.add_page()
pdf.set_fill_color(30, 60, 114)
pdf.rect(0, 0, 210, 297, 'F')
pdf.set_text_color(255, 255, 255)
pdf.set_font('Helvetica', 'B', 28)
pdf.set_y(80)
pdf.cell(0, 14, 'Corrosion Rate Prediction', align='C', ln=True)
pdf.set_font('Helvetica', 'B', 18)
pdf.cell(0, 10, 'ML Internship Study Guide', align='C', ln=True)
pdf.ln(10)
pdf.set_font('Helvetica', '', 13)
pdf.cell(0, 8, 'Industrial Asset Corrosion ML Pipeline', align='C', ln=True)
pdf.ln(8)
pdf.set_font('Helvetica', '', 11)
for line in [
    'Dataset: 100,000 rows | Target: corrosion_rate_mpy',
    'Models: Linear Regression | Random Forest | XGBoost',
    'Tools: Python | scikit-learn | XGBoost | pandas | seaborn',
]:
    pdf.cell(0, 7, line, align='C', ln=True)
pdf.ln(30)
pdf.set_font('Helvetica', 'I', 10)
pdf.cell(0, 7, 'Prepared for Internship Presentation - 2026', align='C', ln=True)

# ── PAGE 2: PROJECT OVERVIEW ──
pdf.add_page()
pdf.section('1. Project Overview')
pdf.body(
    'This project builds a Machine Learning regression model to predict the corrosion rate '
    '(measured in mils per year, mpy) of industrial assets such as pipelines, tanks, and vessels. '
    'Corrosion causes billions of dollars in losses annually. By predicting corrosion rate early, '
    'companies can plan maintenance, reduce failures, and save costs.'
)
pdf.subsection('Business Problem')
pdf.bullet([
    'Predict how fast an asset corrodes given its material, environment, and operating conditions.',
    'Help engineers prioritize which assets need urgent maintenance.',
    'Reduce unexpected failures and safety incidents.',
    'Optimize spending on coatings, inhibitors, and inspections.',
])
pdf.subsection('Dataset Summary')
pdf.bullet([
    'File: synthetic_corrosion_ml_dataset.xlsx  |  Sheet: in',
    'Rows: 100,000  |  Columns: 33',
    'Split column: train (70,058) | val (14,931) | test (15,011)',
    'Target: corrosion_rate_mpy  (range: 0.04 to 56.77 mpy)',
    'Missing: coating (14%) | maintenance (55%) - filled as "None"',
])
pdf.subsection('Key Features Used')
pdf.bullet([
    'Environmental: environment, temperature_c, ph, chloride_g_per_l, oxygen_ppm, humidity_pct',
    'Operational: flow_m_per_s, pressure_bar, exposure_days, inhibitor_ppm',
    'Material: material, material_resistance_index',
    'Protection: coating, coating_efficiency, maintenance',
    'Geometry: wall_thickness_mm, diameter_mm, exposed_area_m2',
])

# ── PAGE 3: ML CONCEPTS ──
pdf.add_page()
pdf.section('2. Machine Learning - Core Concepts')
pdf.subsection('What is Machine Learning?')
pdf.body(
    'Machine Learning (ML) is a branch of Artificial Intelligence where computers learn patterns '
    'from data to make predictions or decisions without being explicitly programmed with rules. '
    'Instead of writing IF-THEN rules, you show the algorithm thousands of examples and it '
    'learns the relationship between inputs (features) and output (target).'
)
pdf.subsection('Types of ML')
pdf.bullet([
    'Supervised Learning: Learn from labeled data (input + correct answer). Our project uses this.',
    'Unsupervised Learning: Find hidden patterns in data with no labels (e.g. clustering).',
    'Reinforcement Learning: Agent learns by trial and error with rewards/penalties.',
])
pdf.subsection('What is Regression?')
pdf.body(
    'Regression is a type of Supervised Learning where the goal is to predict a continuous '
    'numerical value. Examples: predicting house price, temperature, or corrosion rate. '
    'The model learns a mathematical function f(X) = y, where X is features and y is the number to predict.'
)
pdf.bullet([
    'Classification predicts a category (yes/no, type A/B/C).',
    'Regression predicts a number (2.5 mpy, $50,000, 37.2 C).',
    'Our target corrosion_rate_mpy is a continuous number, so we use Regression.',
])
pdf.subsection('The ML Pipeline')
pdf.bullet([
    'Step 1 - Data Collection: Gather raw data (our Excel file).',
    'Step 2 - EDA: Explore data to understand distributions, patterns, missing values.',
    'Step 3 - Preprocessing: Clean data, encode categories, scale numbers.',
    'Step 4 - Modelling: Train algorithms to learn from the data.',
    'Step 5 - Evaluation: Measure how well the model predicts on unseen data.',
    'Step 6 - Deployment: Use the model in production to make predictions.',
])

# ── PAGE 4: EDA ──
pdf.add_page()
pdf.section('3. Exploratory Data Analysis (EDA)')
pdf.body(
    'EDA is the process of analyzing a dataset to summarize its main characteristics, '
    'often using visual methods. It helps you understand the data before building models.'
)
pdf.subsection('Why EDA?')
pdf.bullet([
    'Understand the distribution of the target variable (is it skewed?).',
    'Find correlations between features and the target.',
    'Detect missing values and outliers.',
    'Understand categorical variables (how many unique values?).',
    'Guide feature engineering and preprocessing decisions.',
])
pdf.subsection('Key EDA Findings in Our Project')
pdf.bullet([
    'Target (corrosion_rate_mpy): Right-skewed, mean=2.24, median=1.30, max=56.77 mpy.',
    'Missing: coating 14% (filled as None), maintenance 55% (filled as None).',
    'Top correlated features: base_aggressiveness (+0.47), flow_m_per_s (+0.45), coating_efficiency (-0.45).',
    'Material matters: Carbon Steel corrodes at 3.96 mpy vs Ti Grade 2 at 0.85 mpy.',
    'Environment matters: CO2 Pipeline Wet is most aggressive (up to 9.5 mpy for Carbon Steel).',
    'Coating matters: Uncoated assets ("None") corrode 3-4x faster than coated ones.',
])
pdf.subsection('Common EDA Plots Used')
pdf.bullet([
    'Histogram: Shows distribution shape (normal, skewed, bimodal).',
    'Boxplot: Shows median, quartiles, and outliers for a variable.',
    'Heatmap: Shows correlation between multiple variables at once.',
    'Scatter plot: Shows relationship between two continuous variables.',
    'Bar chart: Shows counts or means of categorical variables.',
])

# ── PAGE 5: PREPROCESSING ──
pdf.add_page()
pdf.section('4. Data Preprocessing')
pdf.body(
    'Raw data is rarely ready for ML. Preprocessing transforms raw data into a clean, '
    'structured format that algorithms can process effectively.'
)
pdf.subsection('Handling Missing Values')
pdf.body(
    'Missing values can cause errors or biased predictions. Strategies depend on why data is missing:'
)
pdf.bullet([
    'Mean/Median Imputation: Replace with average. Good for numeric data with few missing values.',
    'Mode Imputation: Replace with most frequent value. Good for categorical data.',
    'Category "None": If missing means "not applied" (like no coating), treat NaN as a valid category.',
    'Our approach: coating NaN -> "None" (no coating applied), maintenance NaN -> "None" (no maintenance).',
])
pdf.subsection('Categorical Encoding')
pdf.body(
    'ML algorithms work with numbers, not text. We must convert categories to numbers.'
)
pdf.bullet([
    'One-Hot Encoding (pd.get_dummies): Creates a binary column for each category.',
    '  Example: material=[Carbon Steel, Duplex 2205] -> material_Carbon Steel=1,0 + material_Duplex=0,1',
    'Label Encoding: Assigns integer 0,1,2... to each category. Risk: implies ordering that may not exist.',
    'Target Encoding: Replace category with mean of target for that category. Risk of data leakage.',
    'Our approach: One-Hot Encoding for environment, material, coating, maintenance.',
])
pdf.subsection('Feature Scaling')
pdf.body(
    'Algorithms like Linear Regression and SVM are sensitive to feature scale. '
    'Features with large ranges dominate those with small ranges.'
)
pdf.bullet([
    'StandardScaler (Z-score): Subtracts mean, divides by std. Result: mean=0, std=1.',
    'MinMaxScaler: Scales to [0,1] range.',
    'Tree-based models (Random Forest, XGBoost) are scale-invariant - scaling not needed.',
    'Our approach: StandardScaler applied only for Linear Regression.',
])
pdf.subsection('Train / Validation / Test Split')
pdf.bullet([
    'Train set (70%): Model learns parameters from this data.',
    'Validation set (15%): Used during development to tune hyperparameters.',
    'Test set (15%): Final evaluation - model never sees this during training/tuning.',
    'Our dataset already has a "split" column, so we use those predefined splits.',
])

pdf.output('Corrosion_ML_Study_Guide.pdf')
print('Part 1 done - pages 1-5 written.')
