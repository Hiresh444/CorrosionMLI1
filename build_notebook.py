"""Script to generate the corrosion ML notebook using nbformat."""
# pyrefly: ignore [missing-import]
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(src):
    cells.append(nbf.v4.new_markdown_cell(src.strip()))

def code(src):
    cells.append(nbf.v4.new_code_cell(src.strip()))

# ============================================================
# SECTION 1: SETUP & DATA LOADING
# ============================================================
md("""# 🔬 Corrosion Rate Prediction — ML Pipeline
### Predicting `corrosion_rate_mpy` for Industrial Assets

This notebook builds a high-performance regression model on a 100K-row synthetic corrosion dataset.

**Pipeline:** EDA → Preprocessing → Baseline Models → Hyperparameter Tuning → Final Model → Insights""")

code("""# --- 1. Import Libraries ---
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RandomizedSearchCV
import joblib

sns.set_theme(style='whitegrid', palette='viridis', font_scale=1.1)
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['figure.dpi'] = 100

print("✅ All libraries loaded successfully.")""")

code("""# --- 2. Load Data ---
df = pd.read_excel('synthetic_corrosion_ml_dataset.xlsx', sheet_name='in')
print(f"Dataset shape: {df.shape}")
print(f"\\nSplit distribution:\\n{df['split'].value_counts()}")
df.head()""")

code("""# Basic inspection
print("=== Data Types ===")
print(df.dtypes)
print(f"\\n=== Missing Values ===")
print(df.isnull().sum()[df.isnull().sum() > 0])
print(f"\\n=== Numeric Summary ===")
df.describe().round(3)""")

# ============================================================
# SECTION 2: EDA
# ============================================================
md("""## 📊 2. Exploratory Data Analysis (EDA)""")

code("""# 2.1 Target Distribution
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

axes[0].hist(df['corrosion_rate_mpy'], bins=80, color='steelblue', edgecolor='white', alpha=0.8)
axes[0].set_title('Distribution of Corrosion Rate (mpy)')
axes[0].set_xlabel('corrosion_rate_mpy')
axes[0].axvline(df['corrosion_rate_mpy'].mean(), color='red', ls='--', label=f"Mean={df['corrosion_rate_mpy'].mean():.2f}")
axes[0].axvline(df['corrosion_rate_mpy'].median(), color='orange', ls='--', label=f"Median={df['corrosion_rate_mpy'].median():.2f}")
axes[0].legend()

axes[1].hist(np.log1p(df['corrosion_rate_mpy']), bins=80, color='teal', edgecolor='white', alpha=0.8)
axes[1].set_title('Log-Transformed Distribution')
axes[1].set_xlabel('log(1 + corrosion_rate_mpy)')

sns.boxplot(y=df['corrosion_rate_mpy'], ax=axes[2], color='steelblue')
axes[2].set_title('Boxplot of Target')

plt.tight_layout()
plt.show()
print(f"Skewness: {df['corrosion_rate_mpy'].skew():.3f}")
print(f"Kurtosis: {df['corrosion_rate_mpy'].kurtosis():.3f}")""")

code("""# 2.2 Correlation Analysis
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
corr = df[numeric_cols].corr()

# Correlation with target
target_corr = corr['corrosion_rate_mpy'].drop('corrosion_rate_mpy').sort_values(ascending=False)
fig, axes = plt.subplots(1, 2, figsize=(18, 6))

target_corr.plot(kind='barh', ax=axes[0], color=['steelblue' if v > 0 else 'salmon' for v in target_corr])
axes[0].set_title('Feature Correlation with corrosion_rate_mpy')
axes[0].axvline(0, color='black', lw=0.8)

# Heatmap of top features
top_feats = target_corr.abs().nlargest(12).index.tolist() + ['corrosion_rate_mpy']
sns.heatmap(df[top_feats].corr(), annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=axes[1], square=True)
axes[1].set_title('Correlation Heatmap (Top Features)')

plt.tight_layout()
plt.show()""")

code("""# 2.3 Missing Value Analysis
missing = df.isnull().sum()
missing = missing[missing > 0].sort_values(ascending=False)
print("Missing values:")
print(missing)
print(f"\\ncoating missing: {missing.get('coating',0)} ({missing.get('coating',0)/len(df)*100:.1f}%)")
print(f"maintenance missing: {missing.get('maintenance',0)} ({missing.get('maintenance',0)/len(df)*100:.1f}%)")

fig, ax = plt.subplots(figsize=(8, 4))
missing.plot(kind='barh', color='coral', ax=ax)
ax.set_title('Missing Values by Column')
ax.set_xlabel('Count')
plt.tight_layout()
plt.show()""")

code("""# 2.4 Categorical Features Analysis
cat_cols = ['environment', 'material', 'coating', 'maintenance']

fig, axes = plt.subplots(2, 2, figsize=(18, 12))
for ax, col in zip(axes.flat, cat_cols):
    order = df.groupby(col)['corrosion_rate_mpy'].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x=col, y='corrosion_rate_mpy', ax=ax, order=order, palette='viridis')
    ax.set_title(f'Corrosion Rate by {col}')
    ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.show()""")

code("""# 2.5 Key Numeric Features vs Target
num_feats = ['temperature_c', 'ph', 'chloride_g_per_l', 'base_aggressiveness',
             'material_resistance_index', 'coating_efficiency', 'inhibitor_ppm', 'exposure_days']

fig, axes = plt.subplots(2, 4, figsize=(20, 10))
for ax, feat in zip(axes.flat, num_feats):
    sample = df.sample(min(5000, len(df)), random_state=42)
    ax.scatter(sample[feat], sample['corrosion_rate_mpy'], alpha=0.15, s=5, c='steelblue')
    ax.set_xlabel(feat)
    ax.set_ylabel('corrosion_rate_mpy')
    ax.set_title(f'{feat} vs Target')
plt.tight_layout()
plt.show()""")

# ============================================================
# SECTION 3: PREPROCESSING
# ============================================================
md("""## 🛠️ 3. Data Preprocessing""")

code("""# 3.1 Define feature columns
feature_cols = [
    'environment', 'base_aggressiveness', 'temperature_c', 'ph',
    'chloride_g_per_l', 'oxygen_ppm', 'flow_m_per_s', 'humidity_pct',
    'material', 'material_resistance_index',
    'coating', 'coating_efficiency',
    'inhibitor_ppm', 'maintenance',
    'wall_thickness_mm', 'diameter_mm', 'pressure_bar',
    'exposed_area_m2', 'exposure_days'
]
target_col = 'corrosion_rate_mpy'

data = df[feature_cols + [target_col, 'split']].copy()
print(f"Working dataset shape: {data.shape}")""")

code("""# 3.2 Handle Missing Values
# coating & maintenance: NaN means "None applied" — fill with 'None'
data['coating'] = data['coating'].fillna('None')
data['maintenance'] = data['maintenance'].fillna('None')

print("Missing values after handling:")
print(data.isnull().sum()[data.isnull().sum() > 0])
if data.isnull().sum().sum() == 0:
    print("✅ No missing values remain.")""")

code("""# 3.3 Encode Categorical Variables
cat_features = ['environment', 'material', 'coating', 'maintenance']
print("Cardinality:", {c: data[c].nunique() for c in cat_features})

data_encoded = pd.get_dummies(data, columns=cat_features, drop_first=False)
print(f"Shape after encoding: {data_encoded.shape}")""")

code("""# 3.4 Split using the 'split' column
train_df = data_encoded[data_encoded['split'] == 'train'].drop('split', axis=1)
val_df   = data_encoded[data_encoded['split'] == 'val'].drop('split', axis=1)
test_df  = data_encoded[data_encoded['split'] == 'test'].drop('split', axis=1)

X_train = train_df.drop(target_col, axis=1)
y_train = train_df[target_col]
X_val   = val_df.drop(target_col, axis=1)
y_val   = val_df[target_col]
X_test  = test_df.drop(target_col, axis=1)
y_test  = test_df[target_col]

print(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
feature_names = X_train.columns.tolist()""")

code("""# 3.5 Feature Scaling (for Linear Regression)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled   = scaler.transform(X_val)
X_test_scaled  = scaler.transform(X_test)
print("✅ Scaling complete.")""")

# ============================================================
# SECTION 4: BASELINE MODELS
# ============================================================
md("""## 🤖 4. Baseline Models""")

code("""# Helper: evaluation metrics
def evaluate_model(name, y_true, y_pred):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / np.clip(y_true, 1e-8, None))) * 100
    print(f"  {name:25s} | MAE: {mae:.4f} | RMSE: {rmse:.4f} | R²: {r2:.4f} | MAPE: {mape:.2f}%")
    return {'model': name, 'MAE': mae, 'RMSE': rmse, 'R2': r2, 'MAPE': mape}

results = []""")

code("""# 4.1 Linear Regression
lr = LinearRegression()
lr.fit(X_train_scaled, y_train)

print("=== Linear Regression ===")
print("Validation:")
results.append(evaluate_model('LinearRegression (val)', y_val, lr.predict(X_val_scaled)))
print("Test:")
results.append(evaluate_model('LinearRegression (test)', y_test, lr.predict(X_test_scaled)))""")

code("""# 4.2 Random Forest
rf = RandomForestRegressor(n_estimators=200, max_depth=15, min_samples_leaf=5,
                           n_jobs=-1, random_state=42)
rf.fit(X_train, y_train)

print("=== Random Forest ===")
print("Validation:")
results.append(evaluate_model('RandomForest (val)', y_val, rf.predict(X_val)))
print("Test:")
results.append(evaluate_model('RandomForest (test)', y_test, rf.predict(X_test)))""")

code("""# 4.3 XGBoost
xgb = XGBRegressor(n_estimators=500, max_depth=8, learning_rate=0.05,
                   subsample=0.8, colsample_bytree=0.8,
                   reg_alpha=0.1, reg_lambda=1.0,
                   n_jobs=-1, random_state=42, verbosity=0)
xgb.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

print("=== XGBoost ===")
print("Validation:")
results.append(evaluate_model('XGBoost (val)', y_val, xgb.predict(X_val)))
print("Test:")
results.append(evaluate_model('XGBoost (test)', y_test, xgb.predict(X_test)))""")

code("""# 4.4 Baseline Comparison
results_df = pd.DataFrame(results)
print("\\n=== Model Comparison ===")
print(results_df.to_string(index=False))

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, metric in zip(axes, ['MAE', 'RMSE', 'R2']):
    val_res = results_df[results_df['model'].str.contains('val')]
    ax.barh(val_res['model'].str.replace(' (val)',''), val_res[metric], color='steelblue')
    ax.set_title(f'Validation {metric}')
plt.tight_layout()
plt.show()""")

# ============================================================
# SECTION 5: HYPERPARAMETER TUNING
# ============================================================
md("""## ⚡ 5. Hyperparameter Tuning""")

code("""# 5.1 XGBoost Tuning with RandomizedSearchCV
xgb_params = {
    'n_estimators': [300, 500, 800, 1000],
    'max_depth': [6, 8, 10, 12],
    'learning_rate': [0.01, 0.03, 0.05, 0.1],
    'subsample': [0.7, 0.8, 0.9],
    'colsample_bytree': [0.7, 0.8, 0.9],
    'reg_alpha': [0, 0.1, 0.5, 1.0],
    'reg_lambda': [0.5, 1.0, 2.0],
    'min_child_weight': [1, 3, 5],
}

xgb_search = RandomizedSearchCV(
    XGBRegressor(random_state=42, verbosity=0, n_jobs=-1),
    xgb_params, n_iter=30, scoring='neg_mean_absolute_error',
    cv=3, random_state=42, verbose=1, n_jobs=1
)
xgb_search.fit(X_train, y_train)

print(f"\\nBest MAE (CV): {-xgb_search.best_score_:.4f}")
print(f"Best params: {xgb_search.best_params_}")""")

code("""# 5.2 Random Forest Tuning
rf_params = {
    'n_estimators': [200, 300, 500],
    'max_depth': [12, 15, 20, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [2, 5, 10],
    'max_features': ['sqrt', 'log2', 0.5],
}

rf_search = RandomizedSearchCV(
    RandomForestRegressor(random_state=42, n_jobs=-1),
    rf_params, n_iter=20, scoring='neg_mean_absolute_error',
    cv=3, random_state=42, verbose=1, n_jobs=1
)
rf_search.fit(X_train, y_train)

print(f"\\nBest MAE (CV): {-rf_search.best_score_:.4f}")
print(f"Best params: {rf_search.best_params_}")""")

code("""# 5.3 Compare Tuned Models
print("=== Tuned Model Results ===")
tuned_results = []

print("\\n--- Tuned XGBoost ---")
best_xgb = xgb_search.best_estimator_
print("Validation:")
tuned_results.append(evaluate_model('XGBoost-Tuned (val)', y_val, best_xgb.predict(X_val)))
print("Test:")
tuned_results.append(evaluate_model('XGBoost-Tuned (test)', y_test, best_xgb.predict(X_test)))

print("\\n--- Tuned Random Forest ---")
best_rf = rf_search.best_estimator_
print("Validation:")
tuned_results.append(evaluate_model('RF-Tuned (val)', y_val, best_rf.predict(X_val)))
print("Test:")
tuned_results.append(evaluate_model('RF-Tuned (test)', y_test, best_rf.predict(X_test)))

tuned_df = pd.DataFrame(tuned_results)
print("\\n", tuned_df.to_string(index=False))""")

# ============================================================
# SECTION 6: FEATURE IMPORTANCE & RESIDUALS
# ============================================================
md("""## 📈 6. Feature Importance & Error Analysis""")

code("""# 6.1 XGBoost Feature Importance
importances = best_xgb.feature_importances_
feat_imp = pd.DataFrame({'feature': feature_names, 'importance': importances})
feat_imp = feat_imp.sort_values('importance', ascending=False)

fig, ax = plt.subplots(figsize=(10, 8))
top20 = feat_imp.head(20)
ax.barh(top20['feature'][::-1], top20['importance'][::-1], color='steelblue')
ax.set_title('Top 20 Feature Importances (XGBoost)')
ax.set_xlabel('Importance')
plt.tight_layout()
plt.show()

print("\\nTop 10 Features:")
print(feat_imp.head(10).to_string(index=False))""")

code("""# 6.2 Residual Analysis
y_pred_val = best_xgb.predict(X_val)
residuals = y_val - y_pred_val

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Residual distribution
axes[0].hist(residuals, bins=60, color='steelblue', edgecolor='white', alpha=0.8)
axes[0].set_title('Residual Distribution')
axes[0].axvline(0, color='red', ls='--')

# Predicted vs Actual
axes[1].scatter(y_val, y_pred_val, alpha=0.1, s=5, c='steelblue')
axes[1].plot([0, y_val.max()], [0, y_val.max()], 'r--', lw=1.5)
axes[1].set_xlabel('Actual')
axes[1].set_ylabel('Predicted')
axes[1].set_title('Actual vs Predicted')

# Residuals vs Predicted
axes[2].scatter(y_pred_val, residuals, alpha=0.1, s=5, c='steelblue')
axes[2].axhline(0, color='red', ls='--')
axes[2].set_xlabel('Predicted')
axes[2].set_ylabel('Residual')
axes[2].set_title('Residuals vs Predicted')

plt.tight_layout()
plt.show()

print(f"Mean Residual: {residuals.mean():.4f}")
print(f"Std Residual:  {residuals.std():.4f}")""")

# ============================================================
# SECTION 7: FINAL MODEL
# ============================================================
md("""## 🏆 7. Final Model — Training & Saving""")

code("""# 7.1 Train final model on train set, evaluate on val & test
final_model = best_xgb  # Use the best tuned XGBoost

print("=== Final Model Performance ===")
print("\\nValidation Set:")
evaluate_model('Final XGBoost (val)', y_val, final_model.predict(X_val))
print("\\nTest Set:")
evaluate_model('Final XGBoost (test)', y_test, final_model.predict(X_test))""")

code("""# 7.2 Save model, scaler, and predictions
joblib.dump(final_model, 'best_xgboost_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(feature_names, 'feature_names.pkl')

# Save predictions
test_predictions = pd.DataFrame({
    'actual': y_test.values,
    'predicted': final_model.predict(X_test),
    'residual': y_test.values - final_model.predict(X_test)
})
test_predictions.to_csv('test_predictions.csv', index=False)

val_predictions = pd.DataFrame({
    'actual': y_val.values,
    'predicted': final_model.predict(X_val),
    'residual': y_val.values - final_model.predict(X_val)
})
val_predictions.to_csv('val_predictions.csv', index=False)

print("✅ Model saved: best_xgboost_model.pkl")
print("✅ Predictions saved: test_predictions.csv, val_predictions.csv")""")

# ============================================================
# SECTION 8: INSIGHTS
# ============================================================
md("""## 💡 8. Insights & Business Recommendations""")

code("""# 8.1 Top 10 Most Important Features
print("=" * 60)
print("TOP 10 MOST IMPORTANT FEATURES FOR CORROSION RATE")
print("=" * 60)
for i, row in feat_imp.head(10).iterrows():
    print(f"  {feat_imp.head(10).index.tolist().index(i)+1:2d}. {row['feature']:35s} | Importance: {row['importance']:.4f}")

# Visualize
fig, ax = plt.subplots(figsize=(10, 5))
top10 = feat_imp.head(10)
colors = plt.cm.viridis(np.linspace(0.3, 0.9, 10))
ax.barh(top10['feature'][::-1], top10['importance'][::-1], color=colors[::-1])
ax.set_title('🔝 Top 10 Most Important Features', fontsize=14, fontweight='bold')
ax.set_xlabel('Feature Importance (Gain)')
plt.tight_layout()
plt.show()""")

code("""# 8.2 Business Recommendations
recommendations = \"\"\"
╔══════════════════════════════════════════════════════════════════╗
║            BUSINESS RECOMMENDATIONS                             ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Based on the ML model analysis, the key factors driving         ║
║  corrosion rate in industrial assets are:                         ║
║                                                                  ║
║  1. MATERIAL RESISTANCE INDEX — The material's inherent          ║
║     resistance is the strongest predictor. Investing in          ║
║     higher-grade materials (Duplex 2205, Ti Grade 2) can         ║
║     dramatically reduce corrosion.                               ║
║                                                                  ║
║  2. COATING EFFICIENCY — Proper coating application is           ║
║     critical. Ensure coatings are maintained and re-applied      ║
║     on schedule.                                                 ║
║                                                                  ║
║  3. ENVIRONMENTAL FACTORS (pH, Chloride, Temperature) —          ║
║     Aggressive environments (low pH, high chloride, high temp)   ║
║     accelerate corrosion. Monitor and control these where        ║
║     possible.                                                    ║
║                                                                  ║
║  4. INHIBITOR DOSING — Chemical inhibitors significantly         ║
║     reduce corrosion. Optimize dosing schedules.                 ║
║                                                                  ║
║  5. EXPOSURE TIME — Longer exposure = higher corrosion.          ║
║     Implement regular inspection and maintenance cycles.         ║
║                                                                  ║
║  ACTIONS:                                                        ║
║  • Prioritize material upgrades in high-aggressiveness zones     ║
║  • Implement predictive maintenance using this model             ║
║  • Focus coating QC on Marine and Process Brine environments     ║
║  • Monitor pH and chloride levels continuously                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
\"\"\"
print(recommendations)""")

code("""# 8.3 Summary Metrics Table
all_results = results + tuned_results
summary = pd.DataFrame(all_results)
print("\\n=== COMPLETE MODEL COMPARISON ===")
print(summary.to_string(index=False))

# Final visualization
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
val_only = summary[summary['model'].str.contains('val')]
axes[0].barh(val_only['model'], val_only['R2'], color='steelblue')
axes[0].set_title('R² Score (Validation) — Higher is Better')
axes[0].set_xlim(0, 1)

axes[1].barh(val_only['model'], val_only['MAE'], color='coral')
axes[1].set_title('MAE (Validation) — Lower is Better')

plt.tight_layout()
plt.show()
print("\\n✅ Notebook complete! Model and predictions saved.")""")

# ============================================================
# BUILD NOTEBOOK
# ============================================================
nb.cells = cells
nb.metadata = {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.12.0'}
}

with open('Corrosion_Rate_Prediction.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook created with {len(cells)} cells: Corrosion_Rate_Prediction.ipynb")
