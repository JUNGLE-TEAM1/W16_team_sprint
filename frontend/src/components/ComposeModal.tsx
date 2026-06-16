import type {
  ExternalReferencesState,
  FieldChangeHandler,
  FormSubmitHandler,
  PostFormState,
  RelatedPostsState,
} from "../types";
import {
  ExternalReferencesPanel,
  shouldShowExternalReferencesPanel,
} from "./ExternalReferencesPanel";
import { RelatedPostsPanel, shouldShowRelatedPostsPanel } from "./RelatedPostsPanel";

interface ComposeModalProps {
  isOpen: boolean;
  postForm: PostFormState;
  relatedPosts: RelatedPostsState;
  externalReferences: ExternalReferencesState;
  onChange: FieldChangeHandler;
  onSubmit: FormSubmitHandler;
  onFindExternalReferences: () => void | Promise<void>;
  onClose: () => void;
}

export function ComposeModal({
  isOpen,
  postForm,
  relatedPosts,
  externalReferences,
  onChange,
  onSubmit,
  onFindExternalReferences,
  onClose,
}: ComposeModalProps) {
  if (!isOpen) {
    return null;
  }

  const hasSidePanel =
    shouldShowRelatedPostsPanel(relatedPosts) || shouldShowExternalReferencesPanel(externalReferences);

  return (
    <div className="modal-backdrop">
      <section className="modal-panel" role="dialog" aria-modal="true" aria-label="새 게시글 작성">
        <div className="section-heading compact-heading">
          <div>
            <p className="eyebrow">Write</p>
            <h2>새 게시글 작성</h2>
          </div>
          <button className="ghost-button" type="button" onClick={onClose}>
            닫기
          </button>
        </div>

        <div className={hasSidePanel ? "compose-layout has-related" : "compose-layout"}>
          <form className="stack-form" onSubmit={onSubmit}>
            <label className="field">
              <span>Title</span>
              <input name="title" value={postForm.title} onChange={onChange} maxLength={120} required />
            </label>
            <label className="field">
              <span>Content</span>
              <textarea
                name="content"
                value={postForm.content}
                onChange={onChange}
                maxLength={10000}
                required
              />
            </label>
            <label className="field">
              <span>Tags</span>
              <input
                name="tags"
                value={postForm.tags}
                onChange={onChange}
                placeholder="fastapi, auth, sprint"
              />
            </label>
            <div className="compose-ai-actions">
              <button
                className="ghost-button compact-button"
                type="button"
                disabled={externalReferences.isLoading}
                onClick={() => void onFindExternalReferences()}
              >
                외부 참고자료 찾기
              </button>
            </div>
            <button className="submit-button" type="submit">
              게시글 작성
            </button>
          </form>
          <div className="compose-side-panels">
            <RelatedPostsPanel state={relatedPosts} />
            <ExternalReferencesPanel state={externalReferences} />
          </div>
        </div>
      </section>
    </div>
  );
}
