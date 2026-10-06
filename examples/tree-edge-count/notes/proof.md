# Candidate proof

Evidence level: `proof-draft`.

Put $n=|V|$ and induct on integers $n ≥ 1$.

If $n=1$, simplicity excludes loops, so the graph has no edges and $|E|=0=n-1$.

Let $n ≥ 2$, and assume the result for every tree on $n-1$ vertices. Finiteness gives a longest simple path in $T$. Let $v$ be an endpoint. Connectedness implies that $v$ has at least one neighbor. A neighbor outside the path would extend it. A neighbor on the path other than the adjacent path vertex would create a cycle with a segment of the path. Both are impossible, so the degree of $v$ is one.

Delete $v$ and its unique incident edge, obtaining $T'$. Deletion creates no cycle, so $T'$ is acyclic. For vertices $x,y$ of $T'$, connectedness of $T$ gives a simple path between them. The leaf $v$ cannot be an internal vertex, and neither endpoint is $v$, so the path lies in $T'$. Thus $T'$ is connected and is a tree on $n-1$ vertices.

By induction, $T'$ has $n-2$ edges. Restoring the deleted edge gives

$$
|E|=(n-2)+1=n-1.
$$

This completes the induction.
