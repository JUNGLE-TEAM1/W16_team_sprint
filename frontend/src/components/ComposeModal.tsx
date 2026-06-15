import type { FieldChangeHandler, FormSubmitHandler, PostFormState } from "../types";

interface ComposeModalProps {
  isOpen: boolean;
  postForm: PostFormState;
  onChange: FieldChangeHandler;
  onSubmit: FormSubmitHandler;
  onClose: () => void;
}

export function ComposeModal({ isOpen, postForm, onChange, onSubmit, onClose }: ComposeModalProps) {
  if (!isOpen) {
    return null;
  }

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
      </section>
    </div>
  );
}
