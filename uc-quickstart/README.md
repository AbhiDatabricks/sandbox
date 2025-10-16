# Databricks Unity Catalog Quickstart 🌐🚀

**A Collection of Utilities to Accelerate Unity Catalog Setup and Implementation**

Welcome to the **databricks-uc-quickstart** repository! This project is a comprehensive collection of utilities designed to speed up Unity Catalog (UC) deployment and implementation on Databricks. From automated infrastructure setup to industry-specific ABAC demonstrations, these utilities eliminate tedious configuration overhead and accelerate your data governance initiatives.

## 📦 What's Included

This repository contains two main utility collections:

### 1️⃣ **Unity Catalog Infrastructure Deployment** (Terraform)
Automated setup of UC infrastructure with best practices enforced:

- **Catalog Design Defaults**: Pre-configured catalog structures optimized for data governance
- **Workspace Defaults**: Standard workspace configurations for consistent deployments
- **Role Permission Defaults**: Pre-defined role-based access controls following least privilege principles
- **Storage Setup Defaults**: Optimized storage configurations for Unity Catalog
- **Data Sharing Defaults**: Secure data sharing configurations ready for collaboration
- **Volume Defaults**: Standard volume configurations for data storage
- **System Tables**: Automatic system table enablement with appropriate role permissions

### 2️⃣ **ABAC Industry Accelerators** (Notebooks & SQL)
Ready-to-use ABAC (Attribute-Based Access Control) demonstrations for 7 industries:

- **Pre-built masking functions** for data protection (email, phone, SSN, credit cards, etc.)
- **Industry-specific demos**: Retail, Telco, Insurance, Government, Finance, Manufacturing, Healthcare
- **Compliance patterns**: PCI-DSS, HIPAA, GDPR examples
- **Interactive notebooks**: Step-by-step implementation guides
- **Configuration-driven**: Simple YAML-based setup

📘 **For detailed ABAC documentation**, see [utils/abac/industry_templates/README.md](utils/abac/industry_templates/README.md)

## 🌟 Key Benefits

- **Complete UC Setup**: Infrastructure deployment + ABAC implementation in one repository
- **Automated Terraform Deployment**: Effortlessly set up and manage Unity Catalog infrastructure
- **Industry-Ready ABAC**: Pre-built masking functions and policies for 7 industries
- **Instant Setup**: Deploy UC with recommended default configurations
- **Reduced Boilerplate**: Minimal setup—focus more on your core data projects
- **Flexible & Customizable**: Easily adapt configurations to match your unique requirements
- **Compliance Ready**: Built-in patterns for PCI-DSS, HIPAA, and GDPR

## 🏗️ What Gets Deployed

This Terraform quickstart deploys a complete Unity Catalog environment with the following components:

### **Core Infrastructure**
- **3 Unity Catalog Environments**: Production, Development, and Sandbox catalogs
- **Cloud Storage**: Dedicated storage accounts/buckets for each catalog with proper IAM/RBAC
- **External Locations**: Secure storage credential and external location mappings
- **System Schemas**: Access, billing, compute, and storage system tables (if permissions allow)

### **Access Management**
- **User Groups**: Production service principals, developers, and sandbox users
- **Catalog Permissions**: Role-based access control with environment-specific privileges
- **System Schema Grants**: Appropriate permissions for monitoring and governance

### **Compute Resources**
- **Cluster Policies**: Environment-specific policies with cost controls and security settings
- **Clusters**: Pre-configured clusters for each environment with proper access controls

### **Cloud-Specific Resources**

**AWS Deployment:**
- S3 buckets with versioning and encryption
- IAM roles and policies for Unity Catalog access
- Cross-account trust relationships

**Azure Deployment:**
- Storage accounts with containers
- Managed identities and access connectors
- RBAC assignments for Databricks integration

## 🚀 Quick Start

### Option 1: Deploy UC Infrastructure (Terraform)

Follow these steps to rapidly deploy Unity Catalog infrastructure using Terraform:

### 📌 Prerequisites

Ensure you have:

- A Databricks Account
- [Terraform Installed](https://developer.hashicorp.com/terraform/downloads)
- Basic knowledge of Databricks and Terraform

**Workspace Requirements:**
- An existing Databricks workspace is required
- Workspace ID must be provided in the Terraform configuration (see template.tfvars.example)
- The quickstart will configure Unity Catalog resources and permissions within your existing workspace

### 🛠 Installation Steps

1. **Clone this Repository:**

   ```bash
   git clone https://github.com/databrickslabs/sandbox.git
   cd sandbox/uc-quickstart/
   ```

2. **Choose Your Cloud Provider:**
   
   Navigate to the appropriate directory based on your cloud provider:
   
   **For AWS:**
   ```bash
   cd aws/
   ```
   
   **For Azure:**
   ```bash
   cd azure/
   ```

3. **Follow Cloud-Specific Setup:**
   
   Each cloud provider has specific prerequisites and configuration steps detailed in their respective README files:
   - [AWS Setup Instructions](aws/README.md)
   - [Azure Setup Instructions](azure/README.md)

### ✅ Verify Deployment

Once deployment is complete, verify the setup directly within your Databricks workspace to ensure all components are correctly configured.

---

### Option 2: Use ABAC Industry Accelerators

After your Unity Catalog is set up, accelerate ABAC implementation:

1. **Navigate to ABAC utilities:**
   ```bash
   cd utils/abac/industry_templates/
   ```

2. **Choose an industry** (retail, finance, healthcare, etc.)

3. **Follow the guide:**
   - Read the [ABAC README](utils/abac/industry_templates/README.md)
   - Import notebooks to Databricks
   - Configure your catalog in `config.yaml`
   - Run notebooks to create masking functions and demo data

**What you get:**
- Pre-built masking functions (email, phone, SSN, credit cards, etc.)
- Sample data and schemas per industry
- Testing notebooks to validate masking
- Compliance patterns (PCI-DSS, HIPAA, GDPR)

📘 **Full ABAC documentation:** [utils/abac/industry_templates/README.md](utils/abac/industry_templates/README.md)

## 🔧 Need Help?

For cloud-specific troubleshooting and detailed configuration help:
- **AWS Issues:** See [AWS README](aws/README.md#troubleshooting)
- **Azure Issues:** See [Azure README](azure/README.md#troubleshooting)
- **General Questions:** Check the [main documentation](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)

## 📄 License

This project is licensed under the Databricks License—see [LICENSE](../LICENSE) for full details.

