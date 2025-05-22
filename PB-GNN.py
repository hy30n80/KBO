# pitcher_batter_gnn.py

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data, DataLoader
from torch_geometric.nn import SAGEConv
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# --------------------------
# 1. 데이터 준비
# --------------------------
def load_data(edge_csv, node_csv):
    edge_df = pd.read_csv(edge_csv)  # columns: pitcher_id, batter_id, BA, OBP, K%, ...
    node_df = pd.read_csv(node_csv)  # columns: player_id, role, stat1, stat2, ...
    

    # 노드 ID 매핑
    id_map = {pid: i for i, pid in enumerate(node_df['player_id'])}

    # PyG edge_index
    edge_index = torch.tensor([
        [id_map[row['pitcher_id']], id_map[row['batter_id']]]
        for _, row in edge_df.iterrows()
    ]).T.contiguous()

    # 노드 특성
    x = torch.tensor(node_df.drop(columns=['player_id', 'role']).values, dtype=torch.float)

    # 에지 레이블
    y = torch.tensor(edge_df[['BA', 'OBP', 'K%']].values, dtype=torch.float)

    return Data(x=x, edge_index=edge_index), y, edge_df[['pitcher_id', 'batter_id']]

# --------------------------
# 2. GNN 모델 정의
# --------------------------
class PitcherBatterGNN(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, hidden_channels)
        self.regressor = nn.Sequential(
            nn.Linear(hidden_channels * 2, 64),
            nn.ReLU(),
            nn.Linear(64, out_channels)
        )

    def forward(self, x, edge_index, edge_pairs):
        h = F.relu(self.conv1(x, edge_index))
        h = F.relu(self.conv2(h, edge_index))

        h_src = h[edge_pairs[:, 0]]
        h_dst = h[edge_pairs[:, 1]]
        h_pair = torch.cat([h_src, h_dst], dim=1)

        return self.regressor(h_pair)

# --------------------------
# 3. 학습 루프
# --------------------------
def train(model, data, edge_pairs, labels, epochs=100):
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.MSELoss()

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        out = model(data.x, data.edge_index, edge_pairs)
        loss = criterion(out, labels)
        loss.backward()
        optimizer.step()

        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

# --------------------------
# 4. 평가 루프
# --------------------------
def evaluate(model, data, edge_pairs, true_y):
    model.eval()
    with torch.no_grad():
        pred = model(data.x, data.edge_index, edge_pairs)
    
    mse = mean_squared_error(true_y.numpy(), pred.numpy())
    r2 = r2_score(true_y.numpy(), pred.numpy(), multioutput='raw_values')
    print(f"MSE: {mse:.4f}")
    print(f"R2 Scores per target: {r2}")
    return pred

# --------------------------
# 5. 전체 실행
# --------------------------
if __name__ == '__main__':
    edge_csv = 'pitcher_batter_edges.csv'
    node_csv = 'players.csv'

    data, y_all, pairs_df = load_data(edge_csv, node_csv)

    # 학습/테스트 분리 (Unseen Match 기준: pair 기준 분리)
    train_idx, test_idx = train_test_split(range(len(pairs_df)), test_size=0.2, random_state=42)
    edge_pairs = torch.tensor([
        [i, j] for i, j in zip(
            pairs_df.iloc[train_idx]['pitcher_id'].map(lambda pid: data.x.new_tensor([pid])).int(),
            pairs_df.iloc[train_idx]['batter_id'].map(lambda bid: data.x.new_tensor([bid])).int()
        )
    ])

    test_pairs = torch.tensor([
        [i, j] for i, j in zip(
            pairs_df.iloc[test_idx]['pitcher_id'].map(lambda pid: data.x.new_tensor([pid])).int(),
            pairs_df.iloc[test_idx]['batter_id'].map(lambda bid: data.x.new_tensor([bid])).int()
        )
    ])

    y_train = y_all[train_idx]
    y_test = y_all[test_idx]

    model = PitcherBatterGNN(in_channels=data.x.size(1), hidden_channels=64, out_channels=y_all.size(1))

    train(model, data, edge_pairs, y_train, epochs=100)
    print("--- Evaluation ---")
    evaluate(model, data, test_pairs, y_test)
