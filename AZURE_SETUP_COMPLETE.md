# Azure Setup Complete!

## ✅ Resources Created

All Azure resources have been successfully created in the `surgical-outcomes-rg` resource group:

### 1. Azure SQL Database
- **Server**: `surgical-outcomes-sql.database.windows.net`
- **Database**: `surgical-outcomes-db`
- **Tier**: Standard S0 (~£15/month)
- **Admin**: dbadmin
- **Password**: SurgicalDB2024!
- **Status**: ✅ Created and configured

### 2. Azure Storage Account
- **Name**: `surgicaloutcomesstore`
- **Container**: `case-attachments`
- **Purpose**: Store file attachments for cases
- **Status**: ✅ Created

### 3. Azure Function App (API)
- **Name**: `surgical-outcomes-api`
- **URL**: https://surgical-outcomes-api.azurewebsites.net
- **Runtime**: Python 3.11
- **Plan**: Consumption (pay per use)
- **Status**: ✅ Created and configured with environment variables
- **CORS**: Enabled for Static Web App and localhost

### 4. Azure Static Web App (Frontend)
- **Name**: `surgical-outcomes-web`
- **URL**: https://wonderful-tree-0e8ee2803.2.azurestaticapps.net
- **Location**: West Europe
- **Tier**: Free
- **Status**: ✅ Created

## 🔧 Configuration Status

### Function App Settings (✅ Configured)
- ✅ DB_SERVER
- ✅ DB_NAME
- ✅ DB_USER
- ✅ DB_PASSWORD
- ✅ JWT_SECRET (randomly generated)
- ✅ AZURE_STORAGE_CONNECTION_STRING
- ✅ CORS enabled for frontend

### Frontend Configuration (✅ Already configured)
- ✅ API URL points to production Function App
- ✅ Config detects localhost vs production automatically

## 📋 Remaining Manual Steps

### 1. Run Database Schema (REQUIRED)
**You must do this before the app will work!**

1. Go to https://portal.azure.com
2. Navigate to SQL databases → surgical-outcomes-db
3. Click "Query editor" (left menu)
4. Login with:
   - Username: `dbadmin`
   - Password: `SurgicalDB2024!`
5. Open this file: `api-python/schema.sql`
6. Copy all contents
7. Paste into Query editor
8. Click "Run"
9. Verify: You should see "Query succeeded" and 7 tables created

### 2. Set Up GitHub Secrets (REQUIRED for auto-deployment)

Go to: https://github.com/jamesleighton95-code/surgical-outcomes-tracker/settings/secrets/actions

**Add Secret 1:**
- Name: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
- Value: Run this command and copy the entire XML output:
  ```bash
  az functionapp deployment list-publishing-profiles --name surgical-outcomes-api --resource-group surgical-outcomes-rg --xml
  ```

**Add Secret 2:**
- Name: `AZURE_STATIC_WEB_APPS_API_TOKEN`
- Value: `896f6cc2fcabbd57e8853b622a95f6952c112abbc430d7f0774b3d2b4027746002-02edced9-3e31-4cdb-844a-2e99f8c92e4300330260e8ee2803`

### 3. Deploy the Code

Once the GitHub secrets are added, simply push to trigger deployment:
```bash
cd /Users/james/PycharmProjects/PythonProject/surgical-outcomes-tracker
git push origin main
```

GitHub Actions will automatically:
- Deploy the API to Azure Functions
- Deploy the frontend to Static Web App

Check deployment status: https://github.com/jamesleighton95-code/surgical-outcomes-tracker/actions

## 🚀 Testing the Deployment

### After database schema is run and code is deployed:

1. **Visit the frontend**: https://wonderful-tree-0e8ee2803.2.azurestaticapps.net
2. **Click "Sign Up"** and create a test account
3. **Login** with your credentials
4. **Add a test case** to verify everything works
5. **Check the analytics** page

### If something doesn't work:

**Check Function App logs:**
```bash
az functionapp log tail --name surgical-outcomes-api --resource-group surgical-outcomes-rg
```

**Or visit Application Insights:**
https://portal.azure.com/#resource/subscriptions/bc2da700-19df-4a75-8ff0-979a657b7278/resourceGroups/surgical-outcomes-rg/providers/microsoft.insights/components/surgical-outcomes-api/overview

## 📊 Cost Breakdown

Monthly estimated costs (UK South region):
- **SQL Database (Standard S0)**: ~£15/month
- **Function App (Consumption)**: ~£0.20 per 1M requests (likely <£1/month)
- **Static Web App**: FREE
- **Blob Storage**: ~£0.02/GB (minimal)

**Total: ~£15-20/month**

## 🔐 Security Notes

- ✅ Database firewall configured to allow only Azure services
- ✅ HTTPS enforced on all endpoints
- ✅ JWT tokens with 24h expiration
- ✅ Passwords hashed with bcrypt
- ✅ No patient identifiable information stored
- ✅ CORS restricted to your domain

## 📱 Local Development

To run locally (for testing before deployment):

```bash
cd /Users/james/PycharmProjects/PythonProject/surgical-outcomes-tracker

# Install Python dependencies
cd api-python
pip install -r requirements.txt

# Start both services
cd ..
npm start
```

Visit: http://localhost:5001

The app will automatically use the local API (localhost:7071) when running locally.

## 🔄 Updating the Application

To deploy updates:

```bash
# Make your changes
git add .
git commit -m "Description of changes"
git push origin main
```

GitHub Actions will automatically deploy everything!

## 📞 Quick Reference

**Resource Group**: `surgical-outcomes-rg`

**URLs:**
- Frontend: https://wonderful-tree-0e8ee2803.2.azurestaticapps.net
- API: https://surgical-outcomes-api.azurewebsites.net/api
- Azure Portal: https://portal.azure.com

**GitHub:**
- Repository: https://github.com/jamesleighton95-code/surgical-outcomes-tracker
- Actions: https://github.com/jamesleighton95-code/surgical-outcomes-tracker/actions
- Secrets: https://github.com/jamesleighton95-code/surgical-outcomes-tracker/settings/secrets/actions

**Database:**
- Server: surgical-outcomes-sql.database.windows.net
- Database: surgical-outcomes-db
- Admin: dbadmin
- Password: SurgicalDB2024!

## ✅ Next Actions

1. [ ] Run database schema in Azure Portal Query Editor
2. [ ] Add GitHub secrets for deployment
3. [ ] Push code to trigger first deployment
4. [ ] Test the application
5. [ ] Add your first real case!

---

**Status: Ready for deployment once schema is run and GitHub secrets are added!**
