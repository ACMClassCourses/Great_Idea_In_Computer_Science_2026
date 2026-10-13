# 运行：python train.py
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor

torch.manual_seed(0)
batch_size = 64
lr = 0.001
epochs = 3

# 1. 读取 MNIST 数据
train_data = datasets.MNIST(root="data", train=True, download=True, transform=ToTensor())
test_data = datasets.MNIST(root="data", train=False, download=True, transform=ToTensor())
train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_data, batch_size=batch_size, shuffle=False)

# 2. 定义模型：784 -> 64 -> ReLU -> 10
model = nn.Sequential(
    nn.Flatten(),
    nn.Linear(784, 64),
    nn.ReLU(),
    nn.Linear(64, 10),
)

loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=lr)


def train():
    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for X, y in train_loader:
            optimizer.zero_grad()
            logits = model(X)
            loss = loss_fn(logits, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"epoch {epoch + 1}: 平均训练损失 {total_loss / len(train_loader):.4f}")


def test():
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for X, y in test_loader:
            pred = model(X).argmax(dim=1)
            correct += (pred == y).sum().item()
            total += len(y)
    print(f"测试准确率: {correct / total:.4f}")


def show_predictions(n=8):
    model.eval()
    X, y = next(iter(test_loader))
    with torch.no_grad():
        pred = model(X).argmax(dim=1)
    for i in range(n):
        t, p = y[i].item(), pred[i].item()
        mark = "正确" if t == p else "错误"
        print(f"图片 {i}: 真实 {t}, 预测 {p}, {mark}")


if __name__ == "__main__":
    train()
    test()
    show_predictions()
