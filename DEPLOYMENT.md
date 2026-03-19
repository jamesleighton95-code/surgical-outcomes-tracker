# Deployment Guide - Surgical Outcomes Tracker

This guide will walk you through deploying the Surgical Outcomes Tracker to Azure.

## Prerequisites

- Azure account with active subscription
- Azure CLI installed (`az login`)
- Azure Functions Core Tools v4
- GitHub account
- Git installed locally

## Step 1: Create Azure Resources

### 1.1 Create Resource Group

```bash
az group create \
  --name surgical-outcomes-rg \
  --location uksouth
```

### 1.2 Create Azure SQL Database

```bash
# Create SQL Server
az sql server create \
  --name surgical-outcomes-sql \
  --resource-group surgical-outcomes-rg \
  --location uksouth \
  --admin-user dbadmin \
  --admin-password 'YourSecurePassword123!'

# Create Database
az sql db create \
  --resource-group surgical-outcomes-rg \
  --server surgical-outcomes-sql \
  --name surgical-outcomes-db \
  --service-objective S0

# Configure firewall to allow Azure services
az sql server firewall-rule create \
  --resource-group surgical-outcomes-rg \
  --server surgical-outcomes-sql \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### 1.3 Set up Database Schema

1. Go to Azure Portal
2. Navigate to your SQL Database
3. Open Query Editor
4. Login with your admin credentials
5. Copy and paste the contents of `api-python/schema.sql`
6. Execute the script

### 1.4 Create Storage Account

```bash
az storage account create \
  --name surgicaloutcomesstore \
  --resource-group surgical-outcomes-rg \
  --location uksouth \
  --sku Standard_LRS

# Create blob container
az storage container create \
  --name case-attachments \
  --account-name surgicaloutcomesstore \
  --public-access off
```

### 1.5 Create Azure Function App

```bash
az functionapp create \
  --resource-group surgical-outcomes-rg \
  --consumption-plan-location uksouth \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name surgical-outcomes-api \
  --storage-account surgicaloutcomesstore \
  --os-type Linux
```

### 1.6 Create Static Web App

```bash
az staticwebapp create \
  --name surgical-outcomes-web \
  --resource-group surgical-outcomes-rg \
  --location uksouth
```

## Step 2: Configure Environment Variables

### 2.1 Get Connection Strings

```bash
# Database connection string
az sql db show-connection-string \
  --client ado.net \
  --name surgical-outcomes-db \
  --server surgical-outcomes-sql

# Storage connection string
az storage account show-connection-string \
  --name surgicaloutcomesstore \
  --resource-group surgical-outcomes-rg
```

### 2.2 Set Function App Configuration

```bash
# Database settings
az functionapp config appsettings set \
  --name surgical-outcomes-api \
  --resource-group surgical-outcomes-rg \
  --settings \
    "DB_SERVER=surgical-outcomes-sql.database.windows.net" \
    "DB_NAME=surgical-outcomes-db" \
    "DB_USER=dbadmin" \
    "DB_PASSWORD=YourSecurePassword123!" \
    "JWT_SECRET=$(openssl rand -base64 32)" \
    "AZURE_STORAGE_CONNECTION_STRING=<your-storage-connection-string>"
```

### 2.3 Enable CORS

```bash
az functionapp cors add \
  --name surgical-outcomes-api \
  --resource-group surgical-outcomes-rg \
  --allowed-origins https://surgical-outcomes-web.azurestaticapps.net
```

## Step 3: Set up GitHub Repository

### 3.1 Initialize Git Repository

```bash
cd surgical-outcomes-tracker
git init
git add .
git commit -m "Initial commit"
```

### 3.2 Create GitHub Repository

1. Go to github.com
2. Create a new repository (e.g., `surgical-outcomes-tracker`)
3. Push your code:

```bash
git remote add origin https://github.com/yourusername/surgical-outcomes-tracker.git
git branch -M main
git push -u origin main
```

### 3.3 Configure GitHub Secrets

Get the publish profiles and API tokens:

```bash
# Get Function App publish profile
az functionapp deployment list-publishing-profiles \
  --name surgical-outcomes-api \
  --resource-group surgical-outcomes-rg \
  --xml

# Get Static Web App deployment token
az staticwebapp secrets list \
  --name surgical-outcomes-web \
  --resource-group surgical-outcomes-rg
```

Add these as GitHub Secrets:

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`: Paste the XML from Function App
   - `AZURE_STATIC_WEB_APPS_API_TOKEN`: Paste the deployment token

## Step 4: Update Frontend Configuration

Update `build/www/config.js` with your production API URL:

```javascript
const config = {
    apiUrl: isLocalhost
        ? 'http://localhost:7071/api'
        : 'https://surgical-outcomes-api.azurewebsites.net/api',  // Your actual URL
    // ... rest of config
};
```

Commit and push this change:

```bash
git add build/www/config.js
git commit -m "Update production API URL"
git push
```

## Step 5: Deploy

### Option 1: Automatic Deployment (Recommended)

Once you've set up GitHub Actions, simply push to main:

```bash
git push origin main
```

GitHub Actions will automatically:
1. Deploy the API to Azure Functions
2. Deploy the frontend to Azure Static Web Apps

### Option 2: Manual Deployment

#### Deploy API:
```bash
cd api-python
func azure functionapp publish surgical-outcomes-api --python
```

#### Deploy Frontend:
```bash
cd build
swa deploy --app-name surgical-outcomes-web
```

## Step 6: Verify Deployment

### 6.1 Check API Health

Visit: `https://surgical-outcomes-api.azurewebsites.net/api/profile`

You should see an authentication error (401), which is correct.

### 6.2 Check Frontend

Visit: `https://surgical-outcomes-web.azurestaticapps.net`

You should see the landing page.

### 6.3 Test Registration

1. Click "Sign Up"
2. Create a test account
3. Verify you can log in
4. Try adding a case

## Step 7: Configure Custom Domain (Optional)

### 7.1 Add Custom Domain to Static Web App

```bash
az staticwebapp hostname set \
  --name surgical-outcomes-web \
  --resource-group surgical-outcomes-rg \
  --hostname www.yourdomain.com
```

### 7.2 Update DNS

Add a CNAME record pointing to your Static Web App:
- Name: `www`
- Value: `<your-static-web-app>.azurestaticapps.net`

## Monitoring and Troubleshooting

### View Logs

```bash
# Function App logs
az functionapp log tail \
  --name surgical-outcomes-api \
  --resource-group surgical-outcomes-rg

# Or use Application Insights in Azure Portal
```

### Common Issues

1. **Database connection fails**
   - Check firewall rules
   - Verify connection string
   - Ensure database is running

2. **CORS errors**
   - Add your Static Web App URL to CORS allowed origins
   - Check browser console for exact error

3. **Authentication fails**
   - Verify JWT_SECRET is set
   - Check token in browser localStorage

4. **GitHub Actions fails**
   - Verify secrets are set correctly
   - Check Actions tab for error details

## Security Best Practices

1. **Use Azure Key Vault** for secrets in production
2. **Enable Application Insights** for monitoring
3. **Set up Azure AD authentication** for admin access
4. **Regular backups** of SQL Database
5. **Enable SQL Database auditing**
6. **Use managed identities** where possible

## Cost Optimization

- **Function App**: Consumption plan (pay per execution)
- **Static Web App**: Free tier available
- **SQL Database**: Standard S0 (~$15/month) - scale down if needed
- **Storage**: Pay per GB stored and accessed

Estimated monthly cost: $15-30 depending on usage

## Updating the Application

To deploy updates:

```bash
git add .
git commit -m "Description of changes"
git push origin main
```

GitHub Actions will automatically deploy your changes.

## Backup and Recovery

### Database Backup

Azure SQL automatically creates backups. To restore:

```bash
az sql db restore \
  --resource-group surgical-outcomes-rg \
  --server surgical-outcomes-sql \
  --name surgical-outcomes-db-restored \
  --source-database surgical-outcomes-db \
  --time "2024-01-01T00:00:00Z"
```

### Code Backup

Your code is backed up in GitHub. Always commit and push changes.

## Support

For issues:
1. Check Application Insights logs
2. Review GitHub Actions workflow runs
3. Check Azure Portal for resource health
4. Review this deployment guide

## Next Steps

- Set up custom domain
- Configure Azure AD authentication
- Enable Application Insights monitoring
- Set up automated database backups
- Configure alerts for errors
- Add OpenAI API key for custom queries
