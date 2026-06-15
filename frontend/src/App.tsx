import { AppHeader } from "./components/AppHeader";
import { FeedColumn } from "./components/FeedColumn";
import { HeroSection } from "./components/HeroSection";
import { Notice } from "./components/Notice";
import { ReaderSection } from "./components/ReaderSection";
import { SearchToolbar } from "./components/SearchToolbar";
import { TagRail } from "./components/TagRail";
import { WriteColumn } from "./components/WriteColumn";
import { useSprintBoard } from "./hooks/useSprintBoard";

export function App() {
  const board = useSprintBoard();

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
          onSelectPost={board.setSelectedPostId}
          onClearFilters={() => void board.clearFilters()}
        />

        <WriteColumn
          showComposer={board.showComposer}
          editingPostId={board.editingPostId}
          currentUser={board.currentUser}
          draftPost={board.draftPost}
          ragResult={board.ragResult}
          runningRag={board.runningRag}
          savingPost={board.savingPost}
          onOpenComposer={() => board.setShowComposer(true)}
          onCancelEdit={board.cancelEdit}
          onDraftPostChange={board.setDraftPost}
          onRagAssist={() => void board.handleRagAssist()}
          onSavePost={(event) => void board.handleSavePost(event)}
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
