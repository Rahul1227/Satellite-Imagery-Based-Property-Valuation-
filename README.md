# Satellite Imagery-Based Property Valuation

A multimodal deep learning system that predicts property market values by combining tabular features with satellite imagery to capture environmental context and neighborhood characteristics.

## Overview

This project enhances traditional property valuation by incorporating visual environmental context through satellite imagery. The system captures factors like green cover, road networks, proximity to water bodies, and urban density patterns.

## Dataset

### Tabular Data
- Training Set: train.xlsx
- Test Set: test.xlsx
- Key Features: price (target), bedrooms, bathrooms, sqft_living, lat, long

### Visual Data
- Satellite images acquired using Mapbox Static API
- Image specifications: 256x256 pixels, zoom level 18
- Coverage: Satellite view for each property location

## Project Structure

```
GitHub Repository:
├── data_fetcher.py              # Script to download satellite images
├── preprocessing.ipynb          # Data cleaning, image acquisition, feature engineering
├── model_training.ipynb         # Model training and evaluation
└── README.md                    # Project documentation

Google Drive Structure:
Property_Valuation_Project/
├── data/                        # Raw and processed datasets
├── images/                      # Satellite imagery
│   ├── train/
│   └── test/
├── models/                      # Saved model files
└── results/                     # Outputs and visualizations
    ├── predictions.csv
    ├── all_models_comparison.csv
    └── visualizations/
```

## Setup

### Google Colab Environment
This project runs entirely in Google Colab. No local installation required.

### Prerequisites
1. Google Drive access
2. Mapbox API Access Token

### Configuration

1. Add Drive shortcut
- Drive Link: https://drive.google.com/drive/folders/12GUf_nsgH48JqLL1jAE_isvsbgX4zRox?usp=sharing
- Right-click > "Add shortcut to Drive"
- Place in "My Drive" root

2. Set up Mapbox Access Token
- In Colab, go to Secrets (key icon in left sidebar)
- Add secret with name: MAPBOX_ACCESS_TOKEN
- Paste your Mapbox token as value


## Usage

All intermediate results, processed data, trained models, and images are saved to Google Drive. This allows for faster execution as the notebooks can load pre-processed data and trained models directly from Drive instead of reprocessing everything.

### Step 1: Data Preprocessing

Open and run preprocessing.ipynb:

1. Load training and test datasets
2. Fetch satellite images using Mapbox Static API
3. Clean data and handle missing values
4. Perform exploratory data analysis
5. Create train/validation split (80/20)
6. Scale numerical features
7. Save all processed data and images to Drive

### Step 2: Model Training

Open and run model_training.ipynb:

1. Load preprocessed data and images from Drive

2. Train baseline models:
   - Linear Regression
   - Random Forest
   - XGBoost

3. Extract image features using pre-trained CNN (VGG16/ResNet50)

4. Train multimodal models:
   - Early Fusion: Concatenate features before processing
   - Late Fusion: Separate pathways merged at end
   - Hybrid Fusion: Multiple fusion points

5. Evaluate and compare all models using RMSE, R2, MAE

6. Generate Grad-CAM visualizations for explainability

7. Save trained models, predictions, and visualizations to Drive

Since all progress is stored in Drive, you can:
- Resume from any checkpoint
- Skip already completed steps
- Load pre-trained models for quick predictions
- Access results from previous runs

## Model Architectures

### Baseline Models
Use only tabular features (bedrooms, bathrooms, sqft, location, etc.)

### Multimodal Models
Combine tabular features with image features

**Early Fusion**: Concatenate all features at input level

**Late Fusion**: Process separately, combine at output

**Hybrid Fusion**: Multiple fusion points in network

## Drive Structure

### data/
- train.xlsx: Original training data
- test.xlsx: Original test data
- train_processed.csv: Cleaned training data
- test_processed.csv: Cleaned test data

### images/
- train/: Training property images
- test/: Test property images

### models/
- early_fusion_model.h5
- late_fusion_model.h5
- hybrid_fusion_model.h5
- random_forest_model.pkl
- xgboost_model.pkl

### results/
- predictions.csv: Final predictions (id, predicted_price)
- all_models_comparison.csv: Performance metrics
- visualizations/: Training history, comparisons, Grad-CAM

## Technologies

- Google Colab: Development environment
- TensorFlow/Keras: Deep learning
- Scikit-learn: Baseline models
- XGBoost: Gradient boosting
- Pandas, NumPy: Data processing
- Matplotlib, Seaborn: Visualization
- OpenCV, PIL: Image processing
- Mapbox Static API: Satellite image acquisition

## Links

- GitHub: https://github.com/Rahul1227/Satellite-Imagery-Based-Property-Valuation-
- Google Drive: https://drive.google.com/drive/folders/12GUf_nsgH48JqLL1jAE_isvsbgX4zRox?usp=sharing

## Contact

GitHub: @Rahul1227

