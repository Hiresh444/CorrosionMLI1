import nbformat as nbf

with open('Corrosion_Rate_Prediction.ipynb', 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

print(f"Existing cells: {len(nb.cells)}")

cells = []

def md(src): cells.append(nbf.v4.new_markdown_cell(src.strip()))
def code(src): cells.append(nbf.v4.new_code_cell(src.strip()))

# ── SECTION HEADER ──────────────────────────────────────
md("""## 📊 Additional Data Findings & Visualizations

Deeper analysis of coating coverage, exposure distribution, environment breakdown,
maintenance impact, and cost drivers.""")

# ── CELL 1: Pie — Coating Distribution ──────────────────
code("""
# Pie 1: Coating Type Distribution (including None)
df_pie = df.copy()
df_pie['coating'] = df_pie['coating'].fillna('None (Uncoated)')

coating_counts = df_pie['coating'].value_counts()
explode = [0.05] * len(coating_counts)

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

wedge_props = dict(width=0.55, edgecolor='white', linewidth=2)
colors = plt.cm.Set3.colors[:len(coating_counts)]

axes[0].pie(coating_counts, labels=coating_counts.index, autopct='%1.1f%%',
            startangle=140, colors=colors, explode=explode,
            wedgeprops=wedge_props, pctdistance=0.75, textprops={'fontsize': 10})
axes[0].set_title('Coating Type Distribution\\n(% of Total Assets)', fontsize=13, fontweight='bold')

# Mean corrosion rate per coating type
mean_corr_coat = df_pie.groupby('coating')['corrosion_rate_mpy'].mean().sort_values(ascending=True)
bars = axes[1].barh(mean_corr_coat.index, mean_corr_coat.values,
                     color=plt.cm.RdYlGn_r(
                         (mean_corr_coat.values - mean_corr_coat.min()) /
                         (mean_corr_coat.max() - mean_corr_coat.min())
                     ), edgecolor='white', linewidth=0.8)
for bar, val in zip(bars, mean_corr_coat.values):
    axes[1].text(val + 0.05, bar.get_y() + bar.get_height()/2,
                 f'{val:.2f} mpy', va='center', fontsize=9)
axes[1].set_title('Mean Corrosion Rate by Coating Type', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Mean Corrosion Rate (mpy)')
axes[1].axvline(df['corrosion_rate_mpy'].mean(), color='navy', ls='--', lw=1.2, label=f'Overall mean={df["corrosion_rate_mpy"].mean():.2f}')
axes[1].legend(fontsize=9)

plt.suptitle('Coating Coverage & Effectiveness', fontsize=15, fontweight='bold', y=1.01)
plt.tight_layout()
plt.show()

print(f"Uncoated assets: {(df_pie['coating']=='None (Uncoated)').sum():,} ({(df_pie['coating']=='None (Uncoated)').mean()*100:.1f}%)")
print(f"Uncoated mean corrosion: {df_pie[df_pie['coating']=='None (Uncoated)']['corrosion_rate_mpy'].mean():.2f} mpy")
print(f"Best coating (3LPE) mean: {df_pie[df_pie['coating']=='3LPE']['corrosion_rate_mpy'].mean():.2f} mpy")
""")

# ── CELL 2: Pie — Environment Distribution ───────────────
code("""
# Pie 2: Environment Distribution + Risk Level
env_counts = df['environment'].value_counts()
env_mean   = df.groupby('environment')['corrosion_rate_mpy'].mean().sort_values(ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Donut pie
colors_env = plt.cm.tab10.colors[:len(env_counts)]
wedge_props = dict(width=0.55, edgecolor='white', linewidth=2)
axes[0].pie(env_counts[env_mean.index], labels=env_mean.index,
            autopct='%1.1f%%', startangle=90, colors=colors_env,
            wedgeprops=wedge_props, pctdistance=0.75,
            textprops={'fontsize': 9})
axes[0].set_title('Environment Type Distribution\\n(ordered by severity)', fontsize=13, fontweight='bold')

# Bar chart with count + mean corrosion annotated
x = range(len(env_mean))
bar_colors = plt.cm.Reds(
    (env_mean.values - env_mean.min()) / (env_mean.max() - env_mean.min()) * 0.7 + 0.3
)
bars = axes[1].bar(x, env_mean.values, color=bar_colors, edgecolor='white', linewidth=0.8)
axes[1].set_xticks(list(x))
axes[1].set_xticklabels(env_mean.index, rotation=35, ha='right', fontsize=9)
axes[1].set_ylabel('Mean Corrosion Rate (mpy)')
axes[1].set_title('Mean Corrosion Rate by Environment', fontsize=13, fontweight='bold')
for bar, val in zip(bars, env_mean.values):
    axes[1].text(bar.get_x() + bar.get_width()/2, val + 0.05, f'{val:.2f}',
                 ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.show()

print("\\nEnvironment Risk Ranking:")
for i, (env, rate) in enumerate(env_mean.items(), 1):
    count = env_counts[env]
    print(f"  {i}. {env:<22s} | Mean: {rate:.2f} mpy | Count: {count:,}")
""")

# ── CELL 3: Pie — Material Distribution ──────────────────
code("""
# Pie 3: Material Distribution + Resistance Index
mat_counts = df['material'].value_counts()
mat_resist = df.groupby('material')['material_resistance_index'].mean().sort_values(ascending=False)
mat_corr   = df.groupby('material')['corrosion_rate_mpy'].mean().sort_values(ascending=False)

fig, axes = plt.subplots(1, 3, figsize=(20, 7))

# Pie — material counts
colors_mat = plt.cm.Set2.colors[:len(mat_counts)]
wedge_props = dict(width=0.55, edgecolor='white', linewidth=2)
axes[0].pie(mat_counts, labels=mat_counts.index, autopct='%1.1f%%',
            startangle=140, colors=colors_mat, wedgeprops=wedge_props,
            pctdistance=0.75, textprops={'fontsize': 9})
axes[0].set_title('Material Type Distribution', fontsize=12, fontweight='bold')

# Bar — resistance index
colors_r = plt.cm.Greens(
    (mat_resist.values - mat_resist.min()) / (mat_resist.max() - mat_resist.min()) * 0.7 + 0.3
)
bars = axes[1].barh(mat_resist.index[::-1], mat_resist.values[::-1],
                    color=colors_r[::-1], edgecolor='white')
axes[1].set_title('Material Resistance Index\\n(Higher = More Resistant)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Mean Resistance Index')
for bar, val in zip(bars, mat_resist.values[::-1]):
    axes[1].text(val + 0.02, bar.get_y() + bar.get_height()/2,
                 f'{val:.2f}', va='center', fontsize=9)

# Bar — mean corrosion
colors_c = plt.cm.Reds(
    (mat_corr.values - mat_corr.min()) / (mat_corr.max() - mat_corr.min()) * 0.7 + 0.3
)
bars2 = axes[2].barh(mat_corr.index[::-1], mat_corr.values[::-1],
                     color=colors_c[::-1], edgecolor='white')
axes[2].set_title('Mean Corrosion Rate by Material\\n(Lower = Better)', fontsize=12, fontweight='bold')
axes[2].set_xlabel('Mean Corrosion Rate (mpy)')
for bar, val in zip(bars2, mat_corr.values[::-1]):
    axes[2].text(val + 0.02, bar.get_y() + bar.get_height()/2,
                 f'{val:.2f}', va='center', fontsize=9)

plt.suptitle('Material Analysis', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.show()
""")

# ── CELL 4: Pie — Exposed Area Bins ──────────────────────
code("""
# Pie 4: Exposed Area & Wall Thickness Distribution
fig, axes = plt.subplots(1, 3, figsize=(20, 7))

# Bin exposed_area_m2 into quartile ranges
df['area_bin'] = pd.qcut(df['exposed_area_m2'], q=4,
                          labels=['Small\\n(Q1)', 'Medium\\n(Q2)', 'Large\\n(Q3)', 'Very Large\\n(Q4)'])
area_counts = df['area_bin'].value_counts().sort_index()
area_corr   = df.groupby('area_bin', observed=True)['corrosion_rate_mpy'].mean()

colors_a = ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
wedge_props = dict(width=0.55, edgecolor='white', linewidth=2)
axes[0].pie(area_counts, labels=area_counts.index, autopct='%1.1f%%',
            startangle=90, colors=colors_a, wedgeprops=wedge_props,
            pctdistance=0.75, textprops={'fontsize': 10})
axes[0].set_title('Exposed Area Distribution\\n(Quartile Bins)', fontsize=12, fontweight='bold')

# Mean corrosion by area bin
axes[1].bar(area_counts.index, area_corr.values, color=colors_a, edgecolor='white', linewidth=0.8)
axes[1].set_title('Mean Corrosion Rate by Exposed Area', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Exposed Area Bin')
axes[1].set_ylabel('Mean Corrosion Rate (mpy)')
for i, val in enumerate(area_corr.values):
    axes[1].text(i, val + 0.02, f'{val:.2f}', ha='center', fontsize=10, fontweight='bold')

# Wall thickness histogram
axes[2].hist(df['wall_thickness_mm'], bins=40, color='steelblue',
             edgecolor='white', alpha=0.85)
axes[2].axvline(df['wall_thickness_mm'].mean(), color='red', ls='--', lw=1.5,
                label=f'Mean={df["wall_thickness_mm"].mean():.1f} mm')
axes[2].axvline(df['wall_thickness_mm'].median(), color='orange', ls='--', lw=1.5,
                label=f'Median={df["wall_thickness_mm"].median():.1f} mm')
axes[2].set_title('Wall Thickness Distribution', fontsize=12, fontweight='bold')
axes[2].set_xlabel('Wall Thickness (mm)')
axes[2].set_ylabel('Count')
axes[2].legend()

plt.suptitle('Geometry & Exposure Analysis', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.show()

print("\\nExposed Area vs Corrosion Rate:")
for bin_label, mean_rate in area_corr.items():
    print(f"  {str(bin_label):<20s} -> {mean_rate:.2f} mpy")
""")

# ── CELL 5: Pie — Maintenance Distribution ───────────────
code("""
# Pie 5: Maintenance Type Distribution & Impact
df_m = df.copy()
df_m['maintenance_cat'] = df_m['maintenance'].fillna(0)
df_m['maint_label'] = df_m['maintenance'].apply(
    lambda x: 'Cathodic Protection' if x == 1.0
    else ('Periodic Wash' if x == 2.0
    else ('Biocide Dosing' if x == 3.0 else 'No Maintenance'))
    if not pd.isna(x) else 'No Maintenance'
)

# Handle string values in maintenance column
df_m2 = df.copy()
df_m2['maint_label'] = df_m2['maintenance'].fillna('No Maintenance').astype(str)
maint_counts = df_m2['maint_label'].value_counts()
maint_corr   = df_m2.groupby('maint_label')['corrosion_rate_mpy'].mean().sort_values()

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

colors_maint = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6'][:len(maint_counts)]
wedge_props = dict(width=0.55, edgecolor='white', linewidth=2)

axes[0].pie(maint_counts, labels=maint_counts.index, autopct='%1.1f%%',
            startangle=90, colors=colors_maint, wedgeprops=wedge_props,
            pctdistance=0.75, textprops={'fontsize': 10})
axes[0].set_title('Maintenance Strategy Distribution', fontsize=13, fontweight='bold')

bars = axes[1].barh(maint_corr.index, maint_corr.values,
                     color=plt.cm.RdYlGn_r(
                         (maint_corr.values - maint_corr.min()) /
                         (maint_corr.max() - maint_corr.min()) * 0.7 + 0.15
                     ), edgecolor='white')
for bar, val in zip(bars, maint_corr.values):
    axes[1].text(val + 0.02, bar.get_y() + bar.get_height()/2,
                 f'{val:.2f} mpy', va='center', fontsize=10)
axes[1].set_title('Mean Corrosion Rate by Maintenance Type', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Mean Corrosion Rate (mpy)')

plt.suptitle('Maintenance Strategy Analysis', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.show()
""")

# ── CELL 6: Cost Analysis ─────────────────────────────────
code("""
# Cost Analysis: Total cost breakdown and corrosion rate vs cost
cost_cols = ['material_cost_usd', 'coating_cost_usd',
             'inspection_cost_usd', 'expected_failure_cost_usd']
cost_means = df[cost_cols].mean()
cost_labels = ['Material', 'Coating', 'Inspection', 'Failure Cost']

fig, axes = plt.subplots(1, 3, figsize=(20, 7))

# Donut — cost breakdown
colors_cost = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
wedge_props = dict(width=0.55, edgecolor='white', linewidth=2)
axes[0].pie(cost_means, labels=cost_labels, autopct='%1.1f%%',
            startangle=140, colors=colors_cost, wedgeprops=wedge_props,
            pctdistance=0.75, textprops={'fontsize': 11})
axes[0].set_title('Mean Cost Breakdown per Asset\\n(Average across all assets)',
                  fontsize=12, fontweight='bold')

# Scatter: corrosion_rate vs total_cost
sample = df.sample(5000, random_state=42)
sc = axes[1].scatter(sample['corrosion_rate_mpy'], sample['total_cost_usd'],
                     c=sample['corrosion_rate_mpy'], cmap='RdYlGn_r',
                     alpha=0.4, s=15, edgecolors='none')
plt.colorbar(sc, ax=axes[1], label='Corrosion Rate (mpy)')
axes[1].set_xlabel('Corrosion Rate (mpy)')
axes[1].set_ylabel('Total Cost (USD)')
axes[1].set_title('Corrosion Rate vs Total Cost', fontsize=12, fontweight='bold')

# Box: total_cost by environment
env_order = df.groupby('environment')['total_cost_usd'].median().sort_values(ascending=False).index
df.boxplot(column='total_cost_usd', by='environment', ax=axes[2],
           patch_artist=True, vert=True)
axes[2].set_xticklabels(
    [df.groupby('environment')['total_cost_usd'].median().sort_values(ascending=False).index[i]
     for i in range(len(df['environment'].unique()))],
    rotation=40, ha='right', fontsize=8)
axes[2].set_title('Total Cost Distribution by Environment', fontsize=12, fontweight='bold')
axes[2].set_xlabel('Environment')
axes[2].set_ylabel('Total Cost (USD)')
plt.sca(axes[2]); plt.title('Total Cost by Environment')

plt.suptitle('Cost Analysis', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.show()

print(f"\\nCost Summary:")
for col, label in zip(cost_cols, cost_labels):
    print(f"  Mean {label:<20s}: ${df[col].mean():>10,.2f}")
print(f"  Mean Total Cost        : ${df['total_cost_usd'].mean():>10,.2f}")
print(f"  Corr(corrosion, cost)  : {df['corrosion_rate_mpy'].corr(df['total_cost_usd']):.3f}")
""")

# ── CELL 7: Safety Risk & Exposure Days ──────────────────
code("""
# Safety Risk Score Analysis
fig, axes = plt.subplots(2, 3, figsize=(20, 12))

# 1. Safety risk distribution
axes[0,0].hist(df['safety_risk_score'], bins=50, color='#e74c3c',
               edgecolor='white', alpha=0.85)
axes[0,0].set_title('Safety Risk Score Distribution', fontweight='bold')
axes[0,0].set_xlabel('Safety Risk Score')
axes[0,0].axvline(df['safety_risk_score'].mean(), color='navy', ls='--',
                   label=f'Mean={df["safety_risk_score"].mean():.2f}')
axes[0,0].legend()

# 2. Pie: Safety risk quartile buckets
df['risk_bin'] = pd.qcut(df['safety_risk_score'], q=4,
                          labels=['Low\\nRisk', 'Medium\\nRisk', 'High\\nRisk', 'Critical\\nRisk'])
risk_counts = df['risk_bin'].value_counts().sort_index()
colors_risk = ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
wedge_props = dict(width=0.55, edgecolor='white', linewidth=2)
axes[0,1].pie(risk_counts, labels=risk_counts.index, autopct='%1.1f%%',
              startangle=90, colors=colors_risk, wedgeprops=wedge_props,
              pctdistance=0.75, textprops={'fontsize': 10})
axes[0,1].set_title('Safety Risk Level Distribution', fontweight='bold')

# 3. Corrosion rate vs safety risk
sample = df.sample(5000, random_state=42)
axes[0,2].scatter(sample['corrosion_rate_mpy'], sample['safety_risk_score'],
                  alpha=0.3, s=8, c='steelblue')
axes[0,2].set_xlabel('Corrosion Rate (mpy)')
axes[0,2].set_ylabel('Safety Risk Score')
axes[0,2].set_title('Corrosion Rate vs Safety Risk', fontweight='bold')
corr_val = df['corrosion_rate_mpy'].corr(df['safety_risk_score'])
axes[0,2].text(0.05, 0.92, f'r = {corr_val:.3f}', transform=axes[0,2].transAxes,
               fontsize=11, color='red', fontweight='bold')

# 4. Exposure days distribution
axes[1,0].hist(df['exposure_days'], bins=50, color='steelblue',
               edgecolor='white', alpha=0.85)
axes[1,0].set_title('Exposure Days Distribution', fontweight='bold')
axes[1,0].set_xlabel('Exposure Days')
axes[1,0].axvline(df['exposure_days'].mean(), color='red', ls='--',
                   label=f'Mean={df["exposure_days"].mean():.0f} days')
axes[1,0].legend()

# 5. Pie: Exposure duration buckets
df['exp_bin'] = pd.cut(df['exposure_days'],
                        bins=[0, 730, 1825, 3650, df['exposure_days'].max()],
                        labels=['0-2 yrs', '2-5 yrs', '5-10 yrs', '10+ yrs'])
exp_counts = df['exp_bin'].value_counts().sort_index()
colors_exp = ['#3498db', '#2ecc71', '#e67e22', '#e74c3c']
axes[1,1].pie(exp_counts, labels=exp_counts.index, autopct='%1.1f%%',
              startangle=90, colors=colors_exp, wedgeprops=wedge_props,
              pctdistance=0.75, textprops={'fontsize': 10})
axes[1,1].set_title('Asset Exposure Duration Distribution', fontweight='bold')

# 6. Mean corrosion by exposure bin
exp_corr = df.groupby('exp_bin', observed=True)['corrosion_rate_mpy'].mean()
axes[1,2].bar(exp_corr.index, exp_corr.values, color=colors_exp, edgecolor='white')
axes[1,2].set_title('Mean Corrosion Rate by Exposure Duration', fontweight='bold')
axes[1,2].set_xlabel('Exposure Duration')
axes[1,2].set_ylabel('Mean Corrosion Rate (mpy)')
for i, val in enumerate(exp_corr.values):
    axes[1,2].text(i, val + 0.02, f'{val:.2f}', ha='center', fontsize=10, fontweight='bold')

plt.suptitle('Safety Risk & Exposure Duration Analysis', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.show()
""")

# ── CELL 8: Key Findings Summary ──────────────────────────
code("""
# Summary Statistics Table
print("=" * 65)
print("       KEY DATA FINDINGS SUMMARY")
print("=" * 65)

df_c = df.copy()
df_c['coating'] = df_c['coating'].fillna('None')

print("\\n1. COATING IMPACT:")
coat_summary = df_c.groupby('coating')['corrosion_rate_mpy'].agg(['mean','count'])
coat_summary = coat_summary.sort_values('mean')
for coat, row in coat_summary.iterrows():
    print(f"   {coat:<22s}: {row['mean']:.2f} mpy  (n={int(row['count']):,})")

print("\\n2. ENVIRONMENT SEVERITY:")
env_summary = df.groupby('environment')['corrosion_rate_mpy'].mean().sort_values(ascending=False)
for env, rate in env_summary.items():
    print(f"   {env:<22s}: {rate:.2f} mpy")

print("\\n3. MATERIAL PERFORMANCE:")
mat_summary = df.groupby('material')['corrosion_rate_mpy'].mean().sort_values()
for mat, rate in mat_summary.items():
    print(f"   {mat:<22s}: {rate:.2f} mpy")

print("\\n4. COST IMPACT OF HIGH CORROSION:")
high = df[df['corrosion_rate_mpy'] > df['corrosion_rate_mpy'].quantile(0.90)]
low  = df[df['corrosion_rate_mpy'] <= df['corrosion_rate_mpy'].quantile(0.10)]
print(f"   Top 10% corrosion -> Mean total cost: ${high['total_cost_usd'].mean():,.0f}")
print(f"   Bot 10% corrosion -> Mean total cost: ${low['total_cost_usd'].mean():,.0f}")
print(f"   Cost ratio (high/low):  {high['total_cost_usd'].mean()/low['total_cost_usd'].mean():.1f}x")

print("\\n5. SAFETY RISK STATS:")
print(f"   Mean safety risk score: {df['safety_risk_score'].mean():.3f}")
print(f"   Corr(corrosion, safety risk): {df['corrosion_rate_mpy'].corr(df['safety_risk_score']):.3f}")

print("\\n6. EXPOSURE ANALYSIS:")
print(f"   Mean exposure: {df['exposure_days'].mean():.0f} days ({df['exposure_days'].mean()/365:.1f} years)")
print(f"   Corr(exposure_days, corrosion): {df['exposure_days'].corr(df['corrosion_rate_mpy']):.3f}")
print("=" * 65)
""")

nb.cells.extend(cells)

with open('Corrosion_Rate_Prediction.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Done. Notebook now has {len(nb.cells)} cells (+{len(cells)} added).")
