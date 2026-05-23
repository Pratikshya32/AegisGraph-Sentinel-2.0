import torch
from torch_geometric.data import HeteroData
from faker import Faker
import numpy as np
import random

def generate_synthetic_graph(num_accounts=1000, num_devices=500, num_transactions=5000, num_logins=2000):
    """
    Generates a synthetic HeteroData graph object for AegisGraph Sentinel 2.0.
    Simulates a financial network with Accounts, Devices, and their interactions.
    """
    fake = Faker('en_IN')
    data = HeteroData()

    print(f"Generating synthetic graph with {num_accounts} accounts and {num_transactions} transactions...")

    # ==========================================
    # 1. NODE FEATURES
    # ==========================================
    
    # Account Nodes: Features could represent [account_age_days, balance_normalized, risk_score, kyc_status]
    # Shape: (num_accounts, 4)
    account_features = torch.randn((num_accounts, 4), dtype=torch.float32)
    data['account'].x = account_features

    # Device Nodes: Features could represent [device_age, os_risk_score, network_trust]
    # Shape: (num_devices, 3)
    device_features = torch.randn((num_devices, 3), dtype=torch.float32)
    data['device'].x = device_features

    # Assign some dummy labels to accounts (0 = Legit, 1 = Mule Account)
    # Let's say ~5% of accounts are mules
    mule_labels = torch.bernoulli(torch.full((num_accounts,), 0.05)).to(torch.long)
    data['account'].y = mule_labels

    # ==========================================
    # 2. EDGE INDICES & FEATURES
    # ==========================================

    # Edge: Account -> Transacts -> Account
    # edge_index shape: (2, num_transactions)
    src_accounts = torch.randint(0, num_accounts, (num_transactions,))
    dst_accounts = torch.randint(0, num_accounts, (num_transactions,))
    
    # Prevent self-loops (accounts transferring to themselves)
    mask = src_accounts != dst_accounts
    src_accounts = src_accounts[mask]
    dst_accounts = dst_accounts[mask]
    
    transaction_edge_index = torch.stack([src_accounts, dst_accounts], dim=0)
    data['account', 'transacts', 'account'].edge_index = transaction_edge_index

    # Transaction Features: [amount_normalized, hesitation_stress_score, timestamp_offset]
    num_valid_transactions = transaction_edge_index.shape[1]
    transaction_features = torch.randn((num_valid_transactions, 3), dtype=torch.float32)
    data['account', 'transacts', 'account'].edge_attr = transaction_features

    # Edge: Device -> Logs_into -> Account
    # edge_index shape: (2, num_logins)
    src_devices = torch.randint(0, num_devices, (num_logins,))
    dst_login_accounts = torch.randint(0, num_accounts, (num_logins,))
    
    login_edge_index = torch.stack([src_devices, dst_login_accounts], dim=0)
    data['device', 'logs_into', 'account'].edge_index = login_edge_index

    # Login Features: [location_mismatch_score, time_of_day_risk]
    login_features = torch.randn((num_logins, 2), dtype=torch.float32)
    data['device', 'logs_into', 'account'].edge_attr = login_features

    print("Graph generation complete!")
    return data

if __name__ == "__main__":
    # Test the generator when the script is run directly
    graph_data = generate_synthetic_graph()
    
    print("\n--- Graph Summary ---")
    print(graph_data)
    
    # Save the dummy data so other developers can load it instantly
    torch.save(graph_data, 'synthetic_aegis_graph.pt')
    print("\nSaved graph to 'synthetic_aegis_graph.pt'")