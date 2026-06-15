import { AuthPanel } from "./components/AuthPanel";
import { ComposeModal } from "./components/ComposeModal";
import { HeroSearch } from "./components/HeroSearch";
import { PostDetail } from "./components/PostDetail";
import { PostList } from "./components/PostList";
import { StatusMessage } from "./components/StatusMessage";
import { TagFilter } from "./components/TagFilter";
import { TopBar } from "./components/TopBar";
import { useBoardController } from "./hooks/useBoardController";

export default function App() {
  const board = useBoardController();

  return (
    <div className="app-shell">
      <TopBar
        currentUser={board.currentUser}
        onLogoClick={board.goToList}
        onLogout={board.logout}
        onShowLogin={board.showLogin}
        onShowRegister={board.showRegister}
      />

      <AuthPanel
        authView={board.authView}
        authForm={board.authForm}
        onChange={board.updateAuthForm}
        onClose={board.hideAuth}
        onLogin={board.login}
        onRegister={board.register}
      />

      <main>
        {board.selectedPost ? (
          <>
            <StatusMessage status={board.status} />
            <PostDetail
              selectedPost={board.selectedPost}
              comments={board.comments}
              currentUser={board.currentUser}
              isAuthor={board.isAuthor}
              isEditingPost={board.isEditingPost}
              editForm={board.editForm}
              editRelatedPosts={board.editRelatedPosts}
              commentForm={board.commentForm}
              onBackToList={board.goToList}
              onRefreshComments={() => board.loadComments()}
              onLikePost={board.likePost}
              onOpenEditor={board.openPostEditor}
              onDeletePost={board.deletePost}
              onUpdatePost={board.updatePost}
              onEditChange={board.updateEditForm}
              onCancelEdit={board.closePostEditor}
              onCommentChange={board.updateCommentForm}
              onCreateComment={board.createComment}
              onDeleteComment={board.deleteComment}
              onShowLogin={board.showLogin}
            />
          </>
        ) : (
          <>
            <HeroSearch
              search={board.search}
              onSearchChange={board.updateSearch}
              onSubmitSearch={board.submitSearch}
              onClearFilters={board.clearFilters}
            />
            <StatusMessage status={board.status} />
            <TagFilter
              tags={board.tags}
              selectedTagName={board.selectedTagName}
              selectedTag={board.search.tag}
              onFilterByTag={board.filterByTag}
            />
            <PostList
              posts={board.posts}
              pageMeta={board.pageMeta}
              search={board.search}
              onSortChange={board.changeSort}
              onOpenCompose={board.openCompose}
              onSelectPost={board.selectPost}
              onChangePage={board.changePage}
            />
            <ComposeModal
              isOpen={board.isComposeOpen}
              postForm={board.postForm}
              relatedPosts={board.composeRelatedPosts}
              onChange={board.updatePostForm}
              onSubmit={board.createPost}
              onClose={board.closeCompose}
            />
          </>
        )}
      </main>
    </div>
  );
}
