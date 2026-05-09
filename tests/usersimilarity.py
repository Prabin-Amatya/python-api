import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Embedding, Flatten, Concatenate, Dropout
from tensorflow.keras.optimizers import Adam


users = [
    {
        "id": 1,
        "age": 25,
        "job": "student",
        "marital_status": "single",
        "children": 0,
        "gender": "male",
        "income": 0,
        "hobbies": ["coding", "music", "gaming"],
        "autism": 0.2,
        "adhd": 0.1,
        "ocd": 0.0,
        "self_worth_tasks": True,
        "mother": "absent",
        "father": "loving",
        "bullied": True,
        "volatile_family": False,
        "depressed": False,
        "grief": False,
        "reason_productive": "genuine_interest",
        "productivity_struggle": "get_most_done",
        "comeback_plan": "yes",
        "morning_person": True
    },
    {
        "id": 2,
        "age": 27,
        "job": "engineer",
        "marital_status": "single",
        "children": 0,
        "gender": "male",
        "income": 50000,
        "hobbies": ["coding", "music", "reading"],
        "autism": 0.1,
        "adhd": 0.3,
        "ocd": 0.1,
        "self_worth_tasks": False,
        "mother": "loving",
        "father": "absent",
        "bullied": False,
        "volatile_family": False,
        "depressed": False,
        "grief": False,
        "reason_productive": "ego",
        "productivity_struggle": "i_dont_get_things_done",
        "comeback_plan": "no",
        "morning_person": False
    },
]


numeric_features = ['age','income']
categorical_features = ['job','reason_productive']
hobby_set = list(set(h for u in users for h in u['hobbies']))

X_numeric = np.array([[u[f] for f in numeric_features] for u in users], dtype=float)
scaler = StandardScaler()
X_numeric = scaler.fit_transform(X_numeric)

cat_encoders = {}
X_cats = []
for f in categorical_features:
    le = LabelEncoder()
    vals = [u[f] for u in users]
    X_cat = le.fit_transform(vals)
    X_cats.append(X_cat)
    cat_encoders[f] = le

# Hobbies multi-hot
X_hobbies = []
for u in users:
    vec = np.zeros(len(hobby_set))
    for h in u['hobbies']:
        vec[hobby_set.index(h)] = 1
    X_hobbies.append(vec)
X_hobbies = np.array(X_hobbies, dtype=float)


inputs = []
embeddings = []

for i, f in enumerate(categorical_features):
    input_cat = Input(shape=(1,))
    vocab_size = len(cat_encoders[f].classes_)
    emb = Embedding(input_dim=vocab_size, output_dim=min(8, vocab_size), input_length=1)(input_cat)
    emb = Flatten()(emb)
    inputs.append(input_cat)
    embeddings.append(emb)

input_numeric = Input(shape=(X_numeric.shape[1]+X_hobbies.shape[1],))
inputs.append(input_numeric)
embeddings.append(input_numeric)

x = Concatenate()(embeddings)
x = Dense(64, activation='relu')(x)
x = Dropout(0.1)(x)
embedding_layer = Dense(32, activation='tanh', name='user_embedding')(x)  # bottleneck
x = Dense(64, activation='relu')(embedding_layer)
output = Dense(X_numeric.shape[1]+X_hobbies.shape[1], activation='linear')(x)

autoencoder = Model(inputs, output)
encoder = Model(inputs, embedding_layer)

autoencoder.compile(optimizer=Adam(0.01), loss='mse')


X_inputs = [X_cats[i].reshape(-1,1) for i in range(len(X_cats))]
X_inputs.append(np.concatenate([X_numeric,X_hobbies],axis=1))


autoencoder.fit(X_inputs, np.concatenate([X_numeric,X_hobbies],axis=1),
                epochs=500, batch_size=2, verbose=0)


user_embeddings = encoder.predict(X_inputs)

similarity_matrix = cosine_similarity(user_embeddings)
for i, u in enumerate(users):
    sims = similarity_matrix[i].copy()
    sims[i] = -1
    top_idx = sims.argsort()[-3:][::-1]
    print(f"User {u['id']} top similar users:")
    for idx in top_idx:
        print(f"  -> User {users[idx]['id']} (similarity: {sims[idx]:.2f})")