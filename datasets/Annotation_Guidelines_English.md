Below is the complete English translation of the document “糖尿病实体标注和关系标注规范” (“Diabetes Entity Annotation and Relationship Annotation Guidelines”). The translation follows the original structure and content, with each section rendered as accurately as possible. Reputable source: the original document provided by the user citeturn0file0.

---

# Diabetes Entity Annotation and Relationship Annotation Guidelines

## I. Entity Annotation

### 1.1 Disease (Disease)

In these guidelines, “disease” is a broad concept. A disease is defined as an abnormal process of life activity that occurs when homeostatic regulation is disrupted under the influence of certain etiological factors, triggering a series of metabolic, functional, and structural changes. These changes manifest as abnormal symptoms, signs, and behaviors.

**Annotation Principles:**

1. A disease should be one that is classified under ICD-10 or can be confirmed as a disease via reputable sources such as Baidu Baike, medical encyclopedias, etc.
2. The Chinese name, English name, and English abbreviation of a disease are considered three separate entities and should be annotated individually. However, if the English abbreviation or English name is provided as an explanation of the Chinese name, the whole expression should be annotated as a single disease entity (e.g., “糖尿病 (DM)” is annotated as one disease).
3. The type, status, etc., of a disease should be annotated as its staging/classification (Class).
4. Generalized disease terms, such as “chronic disease” or “complications” (when used in a general sense), should not be annotated.

**Annotation Examples:**

- “Currently, type 2 diabetes and its complications have become one of the major diseases threatening public health; controlling blood sugar is one of the important measures to delay the progression of diabetes and the occurrence of its complications.”
- “In these studies, the endpoint HbA1c is controlled around 7.5%. What would be the impact on CVD if, in older diabetic patients with a longer disease course—some of whom already have cardiovascular disease (CVD) or extremely high-risk CVD factors—blood sugar is further reduced?”
- “Studies have shown that as the HbA1c level increases, the risk of developing CVD increases; moreover, patients with a longer history of diabetes experience a smaller reduction in CVD risk after treatment.”

### 1.12 Disease Staging and Classification (Class)

**Annotation Principle:**

- The type or state of a disease should be annotated as its staging/classification (Class).

**Annotation Example:**

- “Type 2 diabetes” is annotated as a whole as a disease, with “Type 2” nested as the disease’s staging/classification.

### 1.2 Etiology (Reason)

Etiology refers to the harmful factors—biological, physical, chemical, social, etc.—that objectively exist externally, or inherent psychological or genetic deficiencies in the human body. When these factors act on the body and induce a pathogenic effect, they are termed etiological factors or causes.

**Annotation Principles:**

1. Etiology specifically refers to these external harmful factors or intrinsic deficiencies that cause disease.
2. Etiology mainly consists of the risk factors for a disease (such as age, body weight, family history, other diseases, etc.), whereas pathogenesis explains how these risk factors influence hormonal changes that eventually lead to the disease. Note the difference between the two. Generally, etiological factors include biological, physico-chemical, nutritional, genetic, congenital, immune, as well as psychological and social factors.

**Annotation Example:**

- “If body weight increases, it may exacerbate insulin resistance and increase the risk of CVD.”  
  Here, “increased body weight” is annotated as the etiological factor, while “insulin resistance” is annotated as the pathogenesis.

### 1.3 Pathogenesis (Pathogenesis)

Pathogenesis refers to the pathological process that occurs when the body is influenced by internal and external environments, resulting in an imbalance. It is termed “mechanism” because every disease follows a certain development pattern and manifests as pathological responses—whether systemic or localized (affecting systems, tissues, organs, or cells). In essence, it explains how risk factors lead to hormonal changes that cause the disease.

**Annotation Principles:**

- Pathogenesis is the process of hormonal changes within the body; it must be distinguished from etiology.

**Annotation Example:**

- “Several years after the onset of type 1 diabetes, most patients experience complete destruction of β-cells, resulting in extremely low islet function and particularly evident clinical manifestations.”  
  Here, “complete destruction of β-cells” is annotated as the pathogenesis.

### 1.4 Clinical Manifestations (Symptom)

Clinical manifestations include both symptoms and signs—that is, what the patient directly experiences and reports, and what is found through medical examination. In these guidelines, “symptom” generally refers to the patient’s own experience or abnormal sensation resulting from abnormal physiological functions caused by the disease. The categories include subjective symptoms (self-reported by the patient) and objective signs (detected by a doctor during examination). Post-treatment symptoms are also included.

**Annotation Principles:**

- Clinical manifestations in these guidelines mainly consist of the patient’s symptoms and signs.

**Annotation Examples:**

- “The patient reports a recent loss of appetite, excessive sleepiness, and sensitivity to cold.”
- “The primary clinical manifestations of Kawasaki disease include fever, congested and chapped lips, and a scarlet fever-like rash.”

### 1.5 Examination Methods (Test)

Examination methods refer to the procedures, processes, or specific tests carried out using laboratory techniques or medical instruments to confirm that a patient has a certain disease or exhibits certain symptoms. These methods provide a basis for clinical diagnosis and treatment. The guidelines include laboratory tests, imaging examinations, auxiliary tests, and other diagnostic projects with significance for disease differentiation.

**Annotation Principles:**

1. Specific examination methods need to be annotated (e.g., MRI, urinalysis, abdominal paracentesis).
2. Broader categories of examinations (e.g., laboratory tests, radiological examinations, pathological examinations) should also be annotated.
3. If the examination involves animal experiments, the specific method should be annotated as well.

**Annotation Example:**

- “Diabetes can be examined through laboratory tests such as urinalysis.”

### 1.6 Examination Indicators (Test_Items)

Examination indicators refer to the specific items within a laboratory test that are categorized as test indicators.

**Annotation Principles:**

1. Specifically annotate the indicators or test items obtained from blood tests in laboratory examinations, such as blood sugar, postprandial blood sugar, and immediate blood sugar.
2. The overall laboratory examination is still categorized under examination methods.

### 1.7 Examination Indicator Values (Test_Value)

Examination indicator values refer to the specific results obtained through laboratory tests or medical instruments.

**Annotation Principles:**

1. The indicator values include the numerical results, symbols, and units.
2. They also include textual descriptions such as “negative,” “positive,” “present/absent,” “increased/decreased,” “high/low,” etc.

**Annotation Examples:**

- “The patient has symptoms of hypoglycemia and blood sugar < 3.3 mmol/L.”
- “HbA1C is controlled at < 6.5%.”

---

## II. Drug-Related Entity Annotation

### 2.1 Drug (Drug)

A drug is defined as any substance used for the prevention, treatment, or diagnosis of diseases. Theoretically, any chemical substance that can affect the physiological functions of organs or the metabolic activities of cells qualifies as a drug. Common categories include steroids, traditional Chinese medicines, chemical drugs, biopharmaceuticals, antibiotics, etc. In annotation, only the specific drug name and its specific category should be annotated.

**Annotation Principles:**

1. Only the specific name of the drug should be annotated.
2. Annotate drugs that belong to a specific category.
3. Do not annotate generalized terms (e.g., “anti-inflammatory drugs” or “anti-diabetic drugs”) when used in a broad sense.

**Annotation Examples:**

- “When selecting insulin secretagogues for treatment, different types can be chosen based on the patient’s blood sugar profile. For instance, for patients whose postprandial blood sugar (PPG) is predominantly elevated, glipizide or meglitinides are advisable.”
- In the phrase “modified-release glipizide tablets,” annotate it as “glipizide modified-release tablets” (modifiers are not separately annotated).

### 2.2 Medication Frequency (Frequency)

Medication frequency refers to how often and how many times a drug is administered within a given period.

**Annotation Principle:**

- Annotate the specific frequency.

**Annotation Examples:**

- “Glipizide is taken once after each meal.”
- “Glipizide modified-release tablets are taken orally twice a day.”
- “Metformin tablets: q6h (once every six hours).”

*Common clinical medication frequency abbreviations include:*

- **qd** (once daily)
- **bid** (twice daily)
- **tid** (three times daily)
- **qid** (four times daily)
- **qod** (every other day)
- **qw** (once weekly)
- **biw** (twice weekly)
- **tiw** (three times weekly)
- **qow** (once every two weeks)
- **2w** (once every two weeks)
- **3w** (once every three weeks)
- **4w** (once every four weeks)
- **q1/2h** (once every 30 minutes)
- **qh** (once hourly)
- **q2h** (once every 2 hours)
- **q3h** (once every 3 hours)
- **q4h** (once every 4 hours)
- **q6h** (once every 6 hours)
- **q8h** (once every 8 hours)
- **q12h** (once every 12 hours)

### 2.3 Medication Dosage (Amount)

The dosage refers to the amount of a drug administered to produce a certain effect, typically the quantity used for preventing or treating a disease.

**Annotation Principle:**

- Annotate the specific numerical value and its unit.

**Annotation Examples:**

- For example, “500mg/d.”
- For instance, “Glipizide, 1 tablet, post-meal, orally, 3 times a day; injectable insulin, 10U, 15 minutes before lunch, intramuscular injection, once a day.”

### 2.4 Medication Administration Method (Method)

There are various routes for drug administration in clinical practice. Common routes include subcutaneous injection, intravenous injection, oral administration, and topical application.

**Annotation Principle:**

- Annotate the specific method of drug administration.

**Annotation Examples:**

- “Insulin is generally administered via intramuscular injection.”
- “Take 1 metformin tablet orally after each meal.”

### 2.5 Non-pharmacological Treatment (Treatment)

Treatment refers to the therapeutic procedures or interventions applied to patients to cure or alleviate symptoms of a disease. In these guidelines, non-pharmacological treatment excludes surgical or drug treatments.

**Annotation Principles:**

1. Annotate non-pharmacological treatments conducted in a hospital setting, which include radiotherapy, traditional Chinese medicine methods, medical nutrition therapy, etc. Examples include “massage,” “acupuncture,” “smoking cessation,” etc.
2. Some lifestyle recommendations are also considered non-pharmacological treatments.

**Annotation Example:**

- “The doctor recommends intensive treatment that includes dietary control and appropriate exercise.”

### 2.6 Surgery (Operation)

Surgery refers to procedures in which a doctor uses medical instruments—such as knives, scissors, and needles—to perform operations (e.g., excision, suturing) on a patient’s body to maintain health. It is the primary treatment method in surgical practice.

**Annotation Principles:**

- When annotating surgery, only the specific surgical method should be noted; generalized terms such as “surgical treatment” need not be annotated.

**Annotation Examples:**

- “Cutting-edge treatment for diabetes is islet cell transplantation surgery to improve the patient’s islet condition.”
- “Patients can also undergo metabolic surgery and other treatment methods.”

### 2.7 Adverse Drug Events (ADE)

Adverse drug events refer to the negative reactions that occur after the administration of a drug or following surgery. This includes both drug-related adverse reactions and post-surgical adverse reactions.

**Annotation Principles:**

1. Clearly distinguish whether an adverse reaction is due to drug administration or surgery.
2. The symptoms of a drug’s adverse reactions are not identical to the symptoms of the disease itself (for example, diabetes may cause weight loss, while oral medications may cause rashes); these differences must be annotated appropriately.

**Annotation Example:**

- “Taking metformin tablets can easily lead to dizziness and symptoms of hypoglycemia.”  
  In this context, these should be annotated as adverse drug reactions.

---

## III. Anatomy and Other Attributes

### 3.1 Anatomy (Anatomy)

Anatomy refers to the structural units composed of various tissues that perform functions. This includes concepts such as body parts, sensory organs, tissues, cells, and embryonic structures.

**Annotation Principles:**

1. Here, anatomy mainly refers to the parts of the body where the disease originates or is involved.
2. Do not annotate anatomical parts that are not related to the disease.
3. If a disease name includes an anatomical part, a nested annotation should be performed with the relationship between the disease and the anatomical part explicitly marked.

**Annotation Examples:**

- “Diabetes can cause a series of lesions that may affect areas such as the retina.”
- In “diabetic foot,” annotate “diabetes” as the disease and “foot” as the anatomical part, and mark the relationship between them.

### 3.2 Severity (Level)

Severity (Level) includes the degree of the disease’s severity as well as the extent of symptom relief after treatment.

### 3.3 Duration (Duration)

Duration mainly refers to how long the symptoms persist, as this information is crucial for diagnosing the condition. It also includes the duration of medication, which must be linked to the specific drug.

**Annotation Principle:**

- Primarily annotate the duration of symptoms.

**Annotation Example:**

- In the phrase “dizzy for one week,” annotate “one week.”

---

## IV. Relationship Annotation

Relationship annotation builds on the annotated named entities. These guidelines focus on disease and drug name entities and assign predefined relationship types to the entities found in medical resources. The goal is to expand the relationships between disease and drug name entities.

### Disease Relationships

1. **Examination Method → Disease (Test_Disease)**
2. **Clinical Manifestations → Disease (Symptom_Disease)**
3. **Non-pharmacological Treatment → Disease (Treatment_Disease)**
4. **Drug Name → Disease (Drug_Disease)**
5. **Anatomy → Disease (Anatomy_Disease)**
6. **Etiology → Disease (Reason_Disease)**
7. **Pathogenesis → Disease (Pathogenesis_Disease)**
8. **Surgery → Disease (Operation_Disease)**
9. **Staging/Class → Disease (Class_Disease)**
10. **Examination Indicators → Disease (Test_Items_Disease)**

### Drug Relationships

1. **Medication Frequency → Drug Name (Frequency_Drug)**
2. **Duration → Drug Name (Duration_Drug)**
3. **Medication Dosage → Drug Name (Amount_Drug)**
4. **Medication Administration Method → Drug Name (Method_Drug)**
5. **Adverse Drug Events → Drug Name (ADE_Drug)**

**Annotation Principles for Relationships:**

1. The extraction of entity relationships is based on a complete sentence.
2. When an entity attribute pertains to both a disease and an adverse reaction, the context should take precedence.

---

*Reputable Source: Original document “糖尿病实体标注和关系标注规范” (annotation-guidelines.pdf) citeturn0file0.*