# CDN Setup Guide

**Story 7.3 - Epic 7: Performance Optimization**

This guide covers the setup and configuration of Content Delivery Network (CDN) for the TreeBeard application to achieve sub-1-second page load times globally.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [AWS CloudFront Setup](#aws-cloudfront-setup)
4. [Google Cloud CDN Setup](#google-cloud-cdn-setup)
5. [Cloudflare Setup](#cloudflare-setup)
6. [Build and Deploy](#build-and-deploy)
7. [Testing and Validation](#testing-and-validation)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The CDN setup provides:

- **Global Edge Distribution**: Serve assets from locations closest to users
- **Cache Optimization**: 1-year cache for versioned assets, 5-minute cache for HTML
- **Automatic Compression**: Gzip/Brotli compression for all text assets
- **HTTPS Enforcement**: Secure connections with TLS 1.2+
- **Cache Busting**: Content-hash-based asset naming
- **DDoS Protection**: Built-in security features

### Performance Targets

| Metric | Target | Strategy |
|--------|--------|----------|
| Page Load Time | < 1s | CDN + asset optimization |
| Cache Hit Rate | > 90% | Proper cache headers + warming |
| TTFB (First Byte) | < 200ms | Edge location proximity |
| Asset Transfer | < 500ms | Compression + CDN |

---

## Prerequisites

### Required

- AWS account (for CloudFront) OR Google Cloud account (for Cloud CDN)
- Domain with DNS control
- SSL/TLS certificate (AWS Certificate Manager or Let's Encrypt)
- Build artifacts from `npm run build`

### Tools

```bash
# AWS CLI
brew install awscli
aws configure

# Google Cloud SDK
brew install google-cloud-sdk
gcloud init

# Cloudflare CLI (optional)
npm install -g wrangler
```

---

## AWS CloudFront Setup

### Step 1: Create S3 Bucket for Static Assets

```bash
# Create bucket
aws s3 mb s3://treebeard-static-assets --region us-east-1

# Enable static website hosting
aws s3 website s3://treebeard-static-assets \
  --index-document index.html \
  --error-document index.html

# Set bucket policy for CloudFront access
cat > bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontServicePrincipal",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::treebeard-static-assets/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT_ID:distribution/DISTRIBUTION_ID"
        }
      }
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket treebeard-static-assets \
  --policy file://bucket-policy.json
```

### Step 2: Request SSL Certificate

```bash
# Request certificate in ACM (must be in us-east-1 for CloudFront)
aws acm request-certificate \
  --domain-name treebeard.com \
  --subject-alternative-names www.treebeard.com \
  --validation-method DNS \
  --region us-east-1

# Note the CertificateArn from output
# Add the DNS validation records to your domain
```

### Step 3: Create CloudFront Distribution

```bash
# Create distribution using config file
aws cloudfront create-distribution \
  --distribution-config file://infrastructure/cloudfront-config.json

# Note the Distribution ID and Domain Name from output
```

**Example cloudfront-config.json:**

```json
{
  "CallerReference": "treebeard-cdn-2024",
  "Comment": "TreeBeard Static Assets CDN",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-treebeard-static-assets",
        "DomainName": "treebeard-static-assets.s3.us-east-1.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        },
        "OriginAccessControlId": "YOUR_OAC_ID"
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-treebeard-static-assets",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 3,
      "Items": ["GET", "HEAD", "OPTIONS"]
    },
    "Compress": true,
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000
  },
  "ViewerCertificate": {
    "ACMCertificateArn": "YOUR_CERTIFICATE_ARN",
    "SSLSupportMethod": "sni-only",
    "MinimumProtocolVersion": "TLSv1.2_2021"
  },
  "Aliases": {
    "Quantity": 2,
    "Items": ["treebeard.com", "www.treebeard.com"]
  }
}
```

### Step 4: Configure DNS

```bash
# Point your domain to CloudFront
# Add CNAME or ALIAS record:
# treebeard.com -> d1234567890abc.cloudfront.net
# www.treebeard.com -> d1234567890abc.cloudfront.net
```

### Step 5: Deploy Assets

```bash
# Build production assets
npm run build

# Upload to S3
aws s3 sync dist/ s3://treebeard-static-assets/ \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "*.html"

# Upload HTML with shorter cache
aws s3 sync dist/ s3://treebeard-static-assets/ \
  --exclude "*" \
  --include "*.html" \
  --cache-control "public, max-age=300, must-revalidate"

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

---

## Google Cloud CDN Setup

### Step 1: Create Storage Bucket

```bash
# Create bucket
gsutil mb -p YOUR_PROJECT_ID \
  -c STANDARD \
  -l US \
  gs://treebeard-static-assets/

# Make bucket public
gsutil iam ch allUsers:objectViewer \
  gs://treebeard-static-assets

# Enable website hosting
gsutil web set -m index.html -e index.html \
  gs://treebeard-static-assets
```

### Step 2: Create Backend Bucket

```bash
# Create backend bucket for CDN
gcloud compute backend-buckets create treebeard-backend \
  --gcs-bucket-name=treebeard-static-assets \
  --enable-cdn \
  --cache-mode=CACHE_ALL_STATIC \
  --default-ttl=86400 \
  --max-ttl=31536000
```

### Step 3: Create Load Balancer

```bash
# Create URL map
gcloud compute url-maps create treebeard-cdn \
  --default-backend-bucket=treebeard-backend

# Create HTTP(S) proxy
gcloud compute target-https-proxies create treebeard-https-proxy \
  --url-map=treebeard-cdn \
  --ssl-certificates=YOUR_SSL_CERT

# Create forwarding rule
gcloud compute forwarding-rules create treebeard-https-rule \
  --global \
  --target-https-proxy=treebeard-https-proxy \
  --ports=443
```

### Step 4: Deploy Assets

```bash
# Build production assets
npm run build

# Upload to Cloud Storage
gsutil -m rsync -r -d dist/ gs://treebeard-static-assets/

# Set cache metadata
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000, immutable" \
  gs://treebeard-static-assets/assets/**

gsutil -m setmeta -h "Cache-Control:public, max-age=300, must-revalidate" \
  gs://treebeard-static-assets/*.html
```

---

## Cloudflare Setup

Cloudflare can be used as an additional CDN layer or as the primary CDN.

### Step 1: Add Site to Cloudflare

1. Log in to Cloudflare dashboard
2. Add site: treebeard.com
3. Update nameservers at your domain registrar

### Step 2: Configure SSL/TLS

```bash
# In Cloudflare dashboard:
# SSL/TLS -> Overview -> Full (Strict)
# SSL/TLS -> Edge Certificates -> Always Use HTTPS: On
# SSL/TLS -> Edge Certificates -> Minimum TLS Version: 1.2
# SSL/TLS -> Edge Certificates -> Automatic HTTPS Rewrites: On
```

### Step 3: Configure Page Rules

```bash
# Page Rule 1: Cache static assets
# URL: treebeard.com/assets/*
# Settings:
#   - Cache Level: Cache Everything
#   - Edge Cache TTL: 1 year
#   - Browser Cache TTL: 1 year

# Page Rule 2: Cache HTML
# URL: treebeard.com/*.html
# Settings:
#   - Cache Level: Cache Everything
#   - Edge Cache TTL: 5 minutes
#   - Browser Cache TTL: 5 minutes

# Page Rule 3: Bypass API
# URL: treebeard.com/api/*
# Settings:
#   - Cache Level: Bypass
```

### Step 4: Enable Performance Features

```bash
# Speed -> Optimization
# - Auto Minify: JS, CSS, HTML ✓
# - Brotli: On ✓
# - Rocket Loader: Off (conflicts with React)
# - Image Optimization: On ✓

# Caching -> Configuration
# - Caching Level: Standard
# - Browser Cache TTL: 4 hours
# - Always Online: On
```

---

## Build and Deploy

### Local Development

```bash
# Development mode (no CDN)
npm run dev
```

### Production Build

```bash
# Build optimized assets
npm run build

# Preview production build locally
npm run preview
```

### Deployment Script

Create `scripts/deploy-cdn.sh`:

```bash
#!/bin/bash
set -e

echo "Building production assets..."
npm run build

echo "Uploading to S3..."
aws s3 sync dist/ s3://treebeard-static-assets/ \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "*.html"

aws s3 sync dist/ s3://treebeard-static-assets/ \
  --exclude "*" \
  --include "*.html" \
  --cache-control "public, max-age=300, must-revalidate"

echo "Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
  --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
  --paths "/*"

echo "Deployment complete!"
```

---

## Testing and Validation

### 1. Test CDN Functionality

```bash
# Test cache headers
curl -I https://treebeard.com/assets/main.abc123.js

# Expected headers:
# Cache-Control: public, max-age=31536000, immutable
# X-Cache: Hit from cloudfront
# Content-Encoding: br (or gzip)
```

### 2. Test from Multiple Locations

```bash
# Use tools like:
# - GTmetrix (https://gtmetrix.com)
# - WebPageTest (https://www.webpagetest.org)
# - Pingdom (https://tools.pingdom.com)

# Test from different regions
curl -w "@curl-format.txt" -o /dev/null -s https://treebeard.com
```

**curl-format.txt:**
```
    time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
   time_pretransfer:  %{time_pretransfer}\n
      time_redirect:  %{time_redirect}\n
 time_starttransfer:  %{time_starttransfer}\n
                    ----------\n
         time_total:  %{time_total}\n
```

### 3. Validate Security Headers

```bash
# Check security headers
curl -I https://treebeard.com

# Should include:
# Strict-Transport-Security: max-age=31536000
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# Content-Security-Policy: ...
# Referrer-Policy: strict-origin-when-cross-origin

# Or use: https://securityheaders.com
```

### 4. Test Cache Hit Rate

```bash
# Monitor cache hit rate in CloudWatch (AWS)
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name CacheHitRate \
  --dimensions Name=DistributionId,Value=$DISTRIBUTION_ID \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average

# Target: >90% cache hit rate
```

---

## Monitoring

### CloudWatch Metrics (AWS)

```bash
# Key metrics to monitor:
# - CacheHitRate (target: >90%)
# - 4xxErrorRate (target: <5%)
# - 5xxErrorRate (target: <1%)
# - BytesDownloaded
# - Requests
# - OriginLatency (target: <200ms)
```

### Setup Alarms

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name treebeard-cache-hit-rate-low \
  --alarm-description "CDN cache hit rate below 80%" \
  --metric-name CacheHitRate \
  --namespace AWS/CloudFront \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80.0 \
  --comparison-operator LessThanThreshold \
  --dimensions Name=DistributionId,Value=$DISTRIBUTION_ID
```

### Logging

```bash
# Enable CloudFront access logs
aws cloudfront update-distribution \
  --id $DISTRIBUTION_ID \
  --logging Bucket=treebeard-cdn-logs.s3.amazonaws.com,\
Prefix=cloudfront/,\
Enabled=true,\
IncludeCookies=false
```

---

## Troubleshooting

### Issue: Low Cache Hit Rate

**Symptoms:** Cache hit rate < 80%

**Solutions:**
1. Check cache headers are set correctly
2. Verify cache behaviors in CloudFront
3. Look for query strings breaking cache
4. Ensure asset URLs include content hash

```bash
# Analyze cache misses
aws cloudfront get-distribution-config \
  --id $DISTRIBUTION_ID \
  --query 'DistributionConfig.DefaultCacheBehavior'
```

### Issue: Stale Content

**Symptoms:** Old version of assets served after deployment

**Solutions:**
1. Create invalidation after deployment
2. Use versioned asset URLs (content hash)
3. Reduce cache TTL for HTML files

```bash
# Force cache invalidation
aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"
```

### Issue: Slow Origin Response

**Symptoms:** High OriginLatency metric

**Solutions:**
1. Enable Origin Shield (AWS CloudFront)
2. Optimize S3 bucket settings
3. Use read replicas for database
4. Enable compression at origin

```bash
# Enable Origin Shield
aws cloudfront update-distribution \
  --id $DISTRIBUTION_ID \
  --origin-shield-enabled \
  --origin-shield-region us-east-1
```

### Issue: SSL/TLS Errors

**Symptoms:** Certificate errors, HTTPS not working

**Solutions:**
1. Verify certificate covers all domain aliases
2. Check certificate is in us-east-1 (CloudFront requirement)
3. Ensure DNS points to CloudFront distribution

```bash
# Check certificate status
aws acm describe-certificate \
  --certificate-arn $CERTIFICATE_ARN \
  --region us-east-1
```

---

## Performance Checklist

- [ ] Assets use content-hash naming
- [ ] Static assets have 1-year cache headers
- [ ] HTML has 5-minute cache headers
- [ ] Compression enabled (Gzip/Brotli)
- [ ] HTTPS enforced everywhere
- [ ] Security headers configured
- [ ] Cache hit rate > 90%
- [ ] Page load time < 1s (P95)
- [ ] CDN monitoring and alerts set up
- [ ] Invalidation strategy in deployment pipeline

---

## Additional Resources

- [AWS CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [Google Cloud CDN Documentation](https://cloud.google.com/cdn/docs)
- [Cloudflare Documentation](https://developers.cloudflare.com/)
- [Web.dev Performance Guide](https://web.dev/performance/)
- [MDN Caching Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)

---

**Next Steps:** See [performance-optimization.md](./performance-optimization.md) for complete performance optimization guide.
