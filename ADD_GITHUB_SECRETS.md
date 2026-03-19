# Add GitHub Secrets for Deployment

Go to: https://github.com/jamesleighton95-code/surgical-outcomes-tracker/settings/secrets/actions

Click "New repository secret" and add these TWO secrets:

## Secret 1: AZURE_FUNCTIONAPP_PUBLISH_PROFILE

**Name**: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`

**Value**: Copy the entire XML output from this command (run it in your terminal):

```bash
az functionapp deployment list-publishing-profiles \
  --name surgical-outcomes-api \
  --resource-group surgical-outcomes-rg \
  --xml
```

It will look like:
```xml
<publishData><publishProfile profileName="surgical-outcomes-api - Web Deploy"...
```

Copy the ENTIRE output (everything from `<publishData>` to `</publishData>`)

---

## Secret 2: AZURE_STATIC_WEB_APPS_API_TOKEN

**Name**: `AZURE_STATIC_WEB_APPS_API_TOKEN`

**Value**:
```
896f6cc2fcabbd57e8853b622a95f6952c112abbc430d7f0774b3d2b4027746002-02edced9-3e31-4cdb-844a-2e99f8c92e4300330260e8ee2803
```

---

## After adding both secrets:

1. Go back to your terminal
2. Push the code to trigger deployment:
   ```bash
   cd /Users/james/PycharmProjects/PythonProject/surgical-outcomes-tracker
   git push origin main
   ```

3. Watch the deployment:
   https://github.com/jamesleighton95-code/surgical-outcomes-tracker/actions

4. Once deployment completes (takes ~3-5 minutes), visit:
   https://wonderful-tree-0e8ee2803.2.azurestaticapps.net

Your app will be live!
