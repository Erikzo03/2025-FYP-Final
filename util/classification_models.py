from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score 

#tries out 4 different classification models 
def train_and_select_model(x_train, y_train, x_val, y_val):
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, solver='liblinear'),
        "KNN": KNeighborsClassifier(n_neighbors=3), 
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42)
    }

    best_model = None
    best_model_name = None
    best_val_acc = 0.0 

    print("\n--- VALIDATION PHASE (Binary Classification) ---")
    if x_train.empty or x_val.empty:
        print("Warning: Training or validation data is empty. Skipping model training.")
        return None, "No Model", 0.0

    if y_val.nunique() < 2 :
        print(f"Warning: Validation target has only {y_val.nunique()} unique class(es). Accuracy might not be meaningful or model fitting might fail for some.")

    for name, model in models.items():
        print(f"\nTraining {name}...")
        try:
            if y_train.nunique() < 2:
                print(f"Skipping {name} as y_train has only {y_train.nunique()} unique classes.")
                continue
            
            model.fit(x_train, y_train)

            if y_val.nunique() < 2: 
                print(f"Warning: y_val has only one class for {name}. Validation accuracy may not be standard.")
               
            val_pred = model.predict(x_val)
            acc = accuracy_score(y_val, val_pred)
            print(f"Validation Accuracy for {name}: {acc:.4f}")

            if acc > best_val_acc:
                best_val_acc = acc
                best_model = model
                best_model_name = name
        except Exception as e:
            print(f"Error training or validating {name}: {e}")
            print(f"y_train unique values: {y_train.unique()}")
            print(f"y_val unique values: {y_val.unique()}")


    if best_model_name:
        print(f"\n✅ Best model from validation: {best_model_name} (Val Accuracy: {best_val_acc:.4f})")
    else:
        print("\nNo model was successfully trained or selected during validation.")
        return None, "No Model Selected", 0.0


    return best_model, best_model_name, best_val_acc