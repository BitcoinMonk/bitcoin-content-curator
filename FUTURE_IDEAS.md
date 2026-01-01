# Future Ideas

## Self-hosted Nitter for Twitter feeds

**Goal:** Add Twitter account following as a content source

**Why Nitter:**
- Free alternative to Twitter API ($100+/month)
- Provides RSS feeds for any public Twitter account
- Open source, can self-host

**Challenges:**
- Twitter actively blocks scrapers
- Public instances are unreliable
- Requires maintenance when Twitter changes their site

**To investigate:**
- [ ] Can Nitter run on beelink server?
- [ ] Docker deployment: https://github.com/zedeus/nitter
- [ ] How often does it break / need updates?
- [ ] Alternative: paid services like RSS.app (~$10/month)

**Implementation (when ready):**
- Add `src/twitter_fetcher.py` to pull from self-hosted Nitter RSS
- Adjust scoring prompt for tweet-length content (curate only, don't rewrite)
- Store curated tweets in Silver Bullet alongside news articles

**Accounts to follow:**
- (add your list here)
