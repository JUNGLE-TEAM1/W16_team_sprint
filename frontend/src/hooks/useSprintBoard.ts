import { useState } from "react";

import { useAuthSession } from "./useAuthSession";
import { useComments } from "./useComments";
import { usePostFeed } from "./usePostFeed";
import { useWriter } from "./useWriter";

export function useSprintBoard() {
  const [error, setError] = useState<string | null>(null);
  const auth = useAuthSession({ setError });
  const feed = usePostFeed({ setError });
  const writer = useWriter({
    filters: feed.filters,
    loadPosts: feed.loadPosts,
    loadTags: feed.loadTags,
    postMeta: feed.postMeta,
    session: auth.session,
    setError,
    setShowAuthPanel: auth.setShowAuthPanel,
  });
  const commentState = useComments({
    selectedPostId: feed.selectedPostId,
    session: auth.session,
    setError,
    setShowAuthPanel: auth.setShowAuthPanel,
  });

  const canEditSelectedPost =
    Boolean(auth.currentUser && feed.selectedPost) &&
    (auth.currentUser?.role === "admin" || feed.selectedPost?.user_id === auth.currentUser?.id);

  return {
    ...auth,
    ...feed,
    ...writer,
    ...commentState,
    canEditSelectedPost,
    error,
  };
}
