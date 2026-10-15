# Deployment rollback

If a deployment increases error rates, pause the rollout. Compare the release identifier with the last healthy revision. Roll back to that revision, then verify readiness and request error rates before resuming traffic.
