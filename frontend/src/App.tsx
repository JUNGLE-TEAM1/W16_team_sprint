import { AppHeader } from "./components/AppHeader";
import { FeedColumn } from "./components/FeedColumn";
import { HeroSection } from "./components/HeroSection";
import { Notice } from "./components/Notice";
import { ReaderSection } from "./components/ReaderSection";
import { SearchToolbar } from "./components/SearchToolbar";
import { TagRail } from "./components/TagRail";
import { WriteColumn } from "./components/WriteColumn";
import { useLifeSupportBoard } from "./hooks/useLifeSupportBoard";

export function App() {
  const board = useLifeSupportBoard();

  function handleOpenMatchedPost(postId: number) {
    void board.selectPost(postId).then((post) => {
      if (!post) return;
      requestAnimationFrame(() => {
        document.querySelector(".readerWrap")?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  }

  return (
    <main className="brunchShell">
      <AppHeader
        currentUser={board.currentUser}
        onRefresh={() => void board.loadPosts(board.postMeta.page)}
        onLogout={() => void board.handleLogout()}
        onToggleAuthPanel={() => board.setShowAuthPanel((open) => !open)}
      />

      <Notice message={board.error} />

      <HeroSection
        currentUser={board.currentUser}
        postMeta={board.postMeta}
        showAuthPanel={board.showAuthPanel}
        authMode={board.authMode}
        authForm={board.authForm}
        authActionLabel={board.authActionLabel}
        savingAuth={board.savingAuth}
        onAuthModeChange={board.setAuthMode}
        onAuthFormChange={board.setAuthForm}
        onAuthSubmit={(event) => void board.handleAuthSubmit(event)}
        onShowAuthPanel={() => board.setShowAuthPanel(true)}
      />

      <SearchToolbar
        filters={board.filters}
        hasActiveFilters={board.hasActiveFilters}
        onFiltersChange={board.setFilters}
        onSearch={(event) => void board.handleSearch(event)}
        onClearFilters={() => void board.clearFilters()}
      />

      <TagRail
        tags={board.tags}
        selectedTag={board.selectedTag}
        onClearFilters={() => void board.clearFilters()}
        onApplyTagFilter={(tagName) => void board.applyTagFilter(tagName)}
      />

      <section className="contentFrame">
        <FeedColumn
          posts={board.posts}
          postMeta={board.postMeta}
          selectedPostId={board.selectedPostId}
          hasActiveFilters={board.hasActiveFilters}
          loadingPosts={board.loadingPosts}
          onLoadPage={(page) => void board.loadPosts(page)}
          onSelectPost={(postId) => void board.selectPost(postId)}
          onClearFilters={() => void board.clearFilters()}
        />

        <WriteColumn
          showComposer={board.showComposer}
          editingPostId={board.editingPostId}
          draftPost={board.draftPost}
          agentResult={board.agentResult}
          ragResult={board.ragResult}
          runningAgent={board.runningAgent}
          runningRag={board.runningRag}
          onOpenComposer={() => board.setShowComposer(true)}
          onCancelEdit={board.cancelEdit}
          onDraftPostChange={board.setDraftPost}
          onWritingAgent={() => void board.handleWritingAgent()}
          onApplyAgentSuggestion={board.applyAgentSuggestion}
          onRagAssist={() => void board.handleRagAssist()}
          onOpenMatchedPost={handleOpenMatchedPost}
        />
      </section>

      <ReaderSection
        selectedPost={board.selectedPost}
        comments={board.comments}
        currentUser={board.currentUser}
        draftComment={board.draftComment}
        loadingComments={board.loadingComments}
        savingComment={board.savingComment}
        canEditSelectedPost={board.canEditSelectedPost}
        onApplyTagFilter={(tagName) => void board.applyTagFilter(tagName)}
        onStartEdit={board.startEdit}
        onDeletePost={(postId) => void board.handleDeletePost(postId)}
        onDraftCommentChange={board.setDraftComment}
        onSaveComment={(event) => void board.handleSaveComment(event)}
        onDeleteComment={(comment) => void board.handleDeleteComment(comment)}
      />
    </main>
  );
}
