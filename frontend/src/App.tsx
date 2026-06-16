import { AuthPanel } from "./components/AuthPanel";
import { ConsultationList } from "./components/ConsultationList";
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
        activeView={board.activeView}
        onLogoClick={board.showSupportInfo}
        onShowSupport={board.showSupportInfo}
        onShowConsultations={board.showConsultations}
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
            {board.activeView === "support" ? (
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
              </>
            ) : (
              <>
                <StatusMessage status={board.status} />
                {board.currentUser ? (
                  <ConsultationList
                    consultations={board.consultations}
                    pageMeta={board.consultationPageMeta}
                    onOpenCompose={board.openCompose}
                    onSelectConsultation={board.selectPost}
                    onChangePage={board.changeConsultationPage}
                  />
                ) : (
                  <section className="posts-section">
                    <div className="locked-panel consultation-empty">
                      <strong>내 상담 기록은 로그인이 필요합니다.</strong>
                      <span>개인 상황과 매칭 기록은 작성자 본인만 볼 수 있도록 분리되어 있습니다.</span>
                      <button className="pill-button highlight" type="button" onClick={board.showLogin}>
                        로그인
                      </button>
                    </div>
                  </section>
                )}
              </>
            )}
            <ComposeModal
              isOpen={board.isComposeOpen}
              postForm={board.postForm}
              relatedPosts={board.composeRelatedPosts}
              externalReferences={board.composeExternalReferences}
              onChange={board.updatePostForm}
              onSubmit={board.createPost}
              onFindExternalReferences={board.findComposeExternalReferences}
              onClose={board.closeCompose}
            />
          </>
        )}
      </main>
    </div>
  );
}
