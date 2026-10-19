# ML architecture

## Algorithm: DBSCAN

Selected because attacker populations are **uneven**. Brute-force bots form dense blobs; a single interactive human is sparse. K-Means forces every IP into k groups and needs a guessed k. DBSCAN leaves true novelties as **noise (cluster -1)**, which we surface as “Unclustered / novel behavior”.

Features per IP (derived, not raw packets):

- login attempts, sessions, commands, downloads, total events  
- events per hour, logins per session, commands per session  

Data is standardized, then clustered every `ML_RETRAIN_SECONDS` (default 300) if at least `ML_MIN_ATTACKERS` IPs exist.

## Labels

The UI shows **Behavior Cluster N** plus an interpretation such as “Credential spraying / brute force”. Interpretations are if-then rules on cluster **feature means**. They are **not** attributions to APT groups or named criminals.

## Limitations

Small demo datasets produce unstable clusters. Live internet noise is better. Retrain is unsupervised; there is no ground-truth accuracy score.
