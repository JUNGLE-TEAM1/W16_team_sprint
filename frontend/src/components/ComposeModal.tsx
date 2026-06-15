import type {
  FieldChangeHandler,
  FormSubmitHandler,
  PostFormState,
  RelatedPostsState,
} from "../types";
import { RelatedPostsPanel, shouldShowRelatedPostsPanel } from "./RelatedPostsPanel";

interface ComposeModalProps {
  isOpen: boolean;
  postForm: PostFormState;
  relatedPosts: RelatedPostsState;
  onChange: FieldChangeHandler;
  onSubmit: FormSubmitHandler;
  onClose: () => void;
}

export function ComposeModal({
  isOpen,
  postForm,
  relatedPosts,
  onChange,
  onSubmit,
  onClose,
}: ComposeModalProps) {
  if (!isOpen) {
    return null;
  }

  const hasRelatedPanel = shouldShowRelatedPostsPanel(relatedPosts);

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

        <div className={hasRelatedPanel ? "compose-layout has-related" : "compose-layout"}>
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
            <button className="submit-button" type="submit">
              게시글 작성
            </button>
          </form>
          <RelatedPostsPanel state={relatedPosts} />
        </div>
      </section>
    </div>
  );
}
