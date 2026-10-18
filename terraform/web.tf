locals {
  web_domain = "app.digizerones.com"
}

# If you already have this data source elsewhere,
# reuse it instead of declaring it twice.
data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "web" {
  bucket = "oms-dev-web-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "web" {
  bucket = aws_s3_bucket.web.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "web" {
  bucket = aws_s3_bucket.web.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_cloudfront_origin_access_control" "web" {
  name                              = "oms-dev-web-oac"
  description                       = "OAC for OMS React application"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

// add acm certificate

resource "aws_acm_certificate" "web" {
  domain_name       = local.web_domain
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "web_certificate_validation" {
  for_each = {
    for dvo in aws_acm_certificate.web.domain_validation_options :
    dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = aws_route53_zone.main.zone_id
  name    = each.value.name
  type    = each.value.type
  records = [each.value.record]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "web" {
  certificate_arn = aws_acm_certificate.web.arn

  validation_record_fqdns = [
    for record in aws_route53_record.web_certificate_validation :
    record.fqdn
  ]
}

// add cloud front

data "aws_cloudfront_cache_policy" "caching_optimized" {
  name = "Managed-CachingOptimized"
}

resource "aws_cloudfront_distribution" "web" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  aliases             = [local.web_domain]
  price_class         = "PriceClass_100"

  origin {
    domain_name              = aws_s3_bucket.web.bucket_regional_domain_name
    origin_id                = "oms-web-s3"
    origin_access_control_id = aws_cloudfront_origin_access_control.web.id
  }

  default_cache_behavior {
    target_origin_id       = "oms-web-s3"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = [
      "GET",
      "HEAD",
      "OPTIONS"
    ]

    cached_methods = [
      "GET",
      "HEAD"
    ]

    cache_policy_id = data.aws_cloudfront_cache_policy.caching_optimized.id

    compress = true
  }

  # Useful once we add React Router.
  # Unknown SPA routes should return index.html.
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.web.certificate_arn
  ssl_support_method       = "sni-only"
  minimum_protocol_version = "TLSv1.2_2021"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  depends_on = [
    aws_acm_certificate_validation.web
  ]
}

// give cloud front permission to read s3

data "aws_iam_policy_document" "web_bucket_policy" {
  statement {
    sid = "AllowCloudFrontRead"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.web.arn}/*"
    ]

    principals {
      type = "Service"

      identifiers = [
        "cloudfront.amazonaws.com"
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"

      values = [
        aws_cloudfront_distribution.web.arn
      ]
    }
  }
}

resource "aws_s3_bucket_policy" "web" {
  bucket = aws_s3_bucket.web.id
  policy = data.aws_iam_policy_document.web_bucket_policy.json
}

// for app.digizerones.com

resource "aws_route53_record" "web" {
  zone_id = aws_route53_zone.main.zone_id
  name    = local.web_domain
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.web.domain_name
    zone_id                = aws_cloudfront_distribution.web.hosted_zone_id
    evaluate_target_health = false
  }
}