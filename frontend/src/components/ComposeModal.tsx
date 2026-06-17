import type {
  FieldChangeHandler,
  FormSubmitHandler,
  PostFormState,
} from "../types";

interface ComposeModalProps {
  isOpen: boolean;
  postForm: PostFormState;
  onChange: FieldChangeHandler;
  onSubmit: FormSubmitHandler;
  onClose: () => void;
}

export function ComposeModal({
  isOpen,
  postForm,
  onChange,
  onSubmit,
  onClose,
}: ComposeModalProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-backdrop">
      <section className="modal-panel" role="dialog" aria-modal="true" aria-label="질문 작성">
        <div className="section-heading compact-heading">
          <div>
            <p className="eyebrow">Pet Care Question</p>
            <h2>질문 작성</h2>
          </div>
          <button className="ghost-button" type="button" onClick={onClose}>
            닫기
          </button>
        </div>

        <div className="compose-layout">
          <form className="stack-form" onSubmit={onSubmit}>
            <label className="field">
              <span>질문 제목</span>
              <input name="title" value={postForm.title} onChange={onChange} maxLength={120} required />
            </label>
            <label className="field">
              <span>반려견 상태와 궁금한 점</span>
              <textarea
                name="content"
                value={postForm.content}
                onChange={onChange}
                maxLength={10000}
                required
              />
            </label>
            <label className="field">
              <span>지역 (선택)</span>
              <input
                name="region"
                value={postForm.region}
                onChange={onChange}
                maxLength={80}
                placeholder="예: 서울 마포구"
              />
            </label>
            <label className="field">
              <span>태그</span>
              <input
                name="tags"
                value={postForm.tags}
                onChange={onChange}
                placeholder="기침, 구토, 피부, 자견, 5개월"
              />
            </label>
            <button className="submit-button" type="submit">
              질문 등록
            </button>
          </form>
        </div>
      </section>
    </div>
  );
}
