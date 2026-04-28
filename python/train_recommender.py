import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import train_test_split


def load_and_prepare_data(csv_path):
    df = pd.read_csv(csv_path)

    # Normalizar nombres de columna a un estándar
    rename_map = {
        "title": "Title",
        "ingredients": "Ingredients",
        "directions": "Instructions",
        "categories": "Category",
        "calories": "Calories",
        "fat": "Fat",
        "protein": "Protein",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    df = df.dropna(subset=["Title", "Ingredients", "Instructions"])
    df = df.drop_duplicates(subset=["Title"]).reset_index(drop=True)

    def join_ingredients(ing_str):
        if isinstance(ing_str, str):
            if "|" in ing_str:
                parts = [x.strip() for x in ing_str.split("|") if x.strip()]
            else:
                parts = [x.strip() for x in ing_str.split(",") if x.strip()]
            return " ".join(parts)
        return ""

    df["Features"] = df["Ingredients"].apply(join_ingredients)

    for col in ["Calories", "Fat", "Protein"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def evaluate_recommender(embeddings_train, embeddings_test, categories_train, categories_test, model):
    # Para cada elemento en test, recuperar top-5 y ver si comparte categoría.
    n_queries = min(len(embeddings_test), 3000)
    indices_test = np.random.choice(len(embeddings_test), n_queries, replace=False)

    precs = []
    sim_values = []

    for i in indices_test:
        query = embeddings_test[i : i + 1]
        dist, neigh = model.kneighbors(query, n_neighbors=5, return_distance=True)
        sim = 1 - dist[0]  # distancia cosine -> similitud aproximada
        sim_values.append(np.mean(sim))

        if "Category" in categories_train and not categories_train.empty:
            target_cat = categories_test.iloc[i]
            hit = (categories_train.iloc[neigh[0]].values == target_cat).astype(int)
            precs.append(np.mean(hit))
        else:
            # fallback: no category, no precision
            precs.append(np.nan)

    precision_mean = np.nanmean(precs)
    if np.isnan(precision_mean):
        precision_mean = float('nan')

    return float(precision_mean), float(np.mean(sim_values))


def plot_history(history, output_path):
    plt.figure(figsize=(8, 4))
    plt.plot(history['n_neighbors'], history['precision'], marker='o', label='Precision@5')
    plt.plot(history['n_neighbors'], history['similarity'], marker='s', label='Avg similarity (1-dist)')
    plt.xlabel('n_neighbors')
    plt.title('Recommender tuning metrics')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_dir = os.path.join(base_dir, "datasets")
    dataset_path = os.path.join(dataset_dir, "RAW_recipes.csv")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"No se encontró RAW_recipes.csv en {dataset_dir}")

    processed_path = os.path.join(dataset_dir, "df_recetas_processed.csv")
    model_dir = os.path.join(base_dir, "models")
    os.makedirs(model_dir, exist_ok=True)

    if os.path.exists(processed_path):
        print(f"Cargando datos procesados desde {processed_path}...")
        df = pd.read_csv(processed_path)
    else:
        print(f"Procesando dataset original {dataset_path}...")
        df = load_and_prepare_data(dataset_path)
        if df.empty:
            raise SystemExit("No hay datos disponibles en el dataset.")
        df.to_csv(processed_path, index=False)
        print(f"Datos procesados guardados en {processed_path}")

    if df.empty:
        raise SystemExit("No hay datos disponibles en el dataset después del procesamiento.")

    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, shuffle=True)

    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    train_embeddings = embedder.encode(train_df['Features'].tolist(), show_progress_bar=True, convert_to_numpy=True)
    test_embeddings = embedder.encode(test_df['Features'].tolist(), show_progress_bar=True, convert_to_numpy=True)

    best_score = -1
    best_model = None
    history = {'n_neighbors': [], 'precision': [], 'similarity': []}

    # Exploramos valores de n_neighbors para elegir el mejor
    for n in [3, 5, 7, 10, 15]:
        nn = NearestNeighbors(n_neighbors=n, metric='cosine')
        nn.fit(train_embeddings)

        precision, avg_sim = evaluate_recommender(train_embeddings, test_embeddings, train_df.get('Category', pd.Series([])), test_df.get('Category', pd.Series([])), nn)

        history['n_neighbors'].append(n)
        history['precision'].append(precision)
        history['similarity'].append(avg_sim)

        print(f"n_neighbors={n} precision={precision:.4f} avg_sim={avg_sim:.4f}")

        # Para la elección de mejor modelo:
        # Si precision es NaN (no hay labels de category), usamos avg_sim
        candidate_score = precision if not np.isnan(precision) else avg_sim

        if candidate_score > best_score:
            best_score = candidate_score
            best_model = nn
            best_n = n

    if best_model is None:
        raise SystemExit("No se pudo entrenar ningún modelo.")

    # Guardar dataframe procesado y configuración selecta.
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    df.to_csv(os.path.join(model_dir, 'df_recetas_processed.csv'), index=False)
    joblib.dump(best_model, os.path.join(model_dir, 'best_nn_model.pkl'))
    joblib.dump({'n_neighbors': best_n, 'metric': 'cosine', 'precision': best_score}, os.path.join(model_dir, 'best_nn_metadata.pkl'))

    # Guardar SentenceTransformer
    embedder_save_dir = os.path.join(model_dir, 'embedder')
    embedder.save(embedder_save_dir)

    history_df = pd.DataFrame(history)
    history_csv_path = os.path.join(model_dir, f'history_{timestamp}.csv')
    history_df.to_csv(history_csv_path, index=False)

    plot_path = os.path.join(model_dir, f'history_plot_{timestamp}.png')
    plot_history(history_df, plot_path)

    print(f"Mejor modelo seleccionado: n_neighbors={best_n}, best_score={best_score:.4f}")
    print(f"Modelos y artefactos guardados en: {os.path.abspath(model_dir)}")
    print(f"Historial guardado en: {history_csv_path}")
    print(f"Gráfico guardado en: {plot_path}")


if __name__ == '__main__':
    main()