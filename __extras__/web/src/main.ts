import './styles.css'

const elForm = document.querySelector('form') as HTMLFormElement
const elLink = document.querySelector('a[download]') as HTMLAnchorElement

elForm.onsubmit = async (ev) => {
  ev.preventDefault()

  const formData = new FormData(elForm)

  const r = await fetch('/api/anki-export', {
    method: 'POST',
    body: formData
  })

  if (r.ok) {
    const filename = (formData.get('file') as File).name
    const format = formData.get('format') as string

    const u = new URL('/api/anki-export', location.origin)
    u.searchParams.set('file', filename)
    u.searchParams.set('format', format)
    elLink.href = u.href
    elLink.download = filename.replace(/\.apkg$/i, '') + '.' + format

    elLink.click()
  }
}
